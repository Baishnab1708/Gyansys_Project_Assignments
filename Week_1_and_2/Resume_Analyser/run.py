import uuid
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from app.vector_store import resume_store
from app.chains import jd_parser_chain, resume_parser_chain, llm_evaluator_chain, reranker_chain
from app.scoring import (
    compute_semantic_score,
    compute_skill_match_score,
    compute_experience_score,
    compute_aggregate_score
)
from app.schemas import RankedCandidate, ScoringSignals



RESUME_FOLDER = "./resumes"

JD_TEXT = """
Job Title: SAP ABAP Developer
Experience: 2–6 Years
Location: Open / Hybrid / Onsite
Employment Type: Full-time
Job Summary

We are looking for a skilled SAP ABAP Developer to design, develop, and support SAP applications. The ideal candidate should have strong hands-on experience in ABAP programming, SAP modules integration, and performance optimization, with the ability to work closely with functional consultants and business stakeholders.

Key Responsibilities

Design, develop, test, and support SAP ABAP programs including Reports, Interfaces, Conversions, Enhancements, and Forms (RICEFW)

Develop and enhance ALV reports, classical & interactive reports

Work on Data Dictionary objects (Tables, Views, Indexes, Domains, Data Elements)

Develop and maintain SmartForms, SAP Scripts, and Adobe Forms

Implement User Exits, Customer Exits, BADIs, Enhancements, and BAPIs

Develop and support RFCs, IDOCs, BDCs, and file-based interfaces

Optimize ABAP code for performance and scalability

Collaborate with functional consultants to translate business requirements into technical solutions

Perform debugging, issue analysis, and production support

Follow SAP best practices, coding standards, and documentation guidelines

Required Skills

Strong proficiency in ABAP/4

Hands-on experience with Reports, ALV, Module Pool, and Dialog Programming

Good knowledge of SAP SD / MM / FI / CO / HR (any one or more modules)

Experience with Enhancements Framework

Solid understanding of Open SQL, Internal Tables, and Performance Tuning

Experience with Forms (SmartForms / Adobe Forms)

Familiarity with IDOC, RFC, BAPI, BDC

Good debugging and troubleshooting skills

Good to Have

Experience with ABAP on HANA

Knowledge of CDS Views, AMDP, OData, and SAP Fiori integration

Exposure to S/4HANA migration projects

Experience working in Agile / Scrum environments

Basic understanding of SAP Security and Transport Management

Educational Qualifications

Bachelor’s degree in Computer Science / IT / Engineering or equivalent

SAP ABAP Certification (optional but preferred)

Soft Skills

Strong analytical and problem-solving skills

Good communication and stakeholder management

Ability to work independently and in a team

Willingness to learn new SAP technologies
"""


def main():
    print("\n" + "=" * 60)
    print("RESUME ANALYSER PIPELINE")
    print("=" * 60)
    
    # Step 1: Check and ingest resumes
    print("\n[STEP 1] Checking resume vector store...")
    
    collection_info = resume_store.client.get_collection(resume_store.COLLECTION_NAME)
    existing_count = collection_info.points_count
    
    if existing_count == 0:
        print(f"  No resumes in store. Ingesting from {RESUME_FOLDER}...")
        count = resume_store.ingest_resumes(RESUME_FOLDER)
        print(f"  Ingested {count} resumes")
    else:
        print(f"  Found {existing_count} resumes already vectorized")
    
    # Step 2: Parse JD
    print("\n[STEP 2] Parsing job description...")
    parsed_jd = jd_parser_chain.parse(JD_TEXT)
    print(f"  JD Summary: {parsed_jd.summary[:100]}...")
    print(f"  Must-have skills: {parsed_jd.must_have_skills}")
    print(f"  Experience required: {parsed_jd.min_experience_years}-{parsed_jd.max_experience_years} years")
    
    # Step 3: Search resumes with query-time slicing
    print("\n[STEP 3] Searching resumes (Qdrant with query-time slicing)...")
    candidates = resume_store.search_resumes(JD_TEXT, top_k_stage1=7, top_k_final=4)
    
    if not candidates:
        print("  No resumes found. Add PDFs to ./resumes/ folder.")
        return
    
    print(f"  Stage 1: Retrieved top 7 candidates (256-dim)")
    print(f"  Stage 2: Reranked to top {len(candidates)} (full-dim)")
    
    for i, (filename, text, score) in enumerate(candidates):
        print(f"    {i+1}. {filename} (similarity: {score:.3f})")
    
    # Step 4: Parse resumes with LLM
    print("\n[STEP 4] Parsing top candidates with LLM...")
    parsed_candidates = []
    
    for idx, (filename, text, search_score) in enumerate(candidates):
        candidate_id = f"c{idx + 1}_{uuid.uuid4().hex[:6]}"
        parsed = resume_parser_chain.parse(text, candidate_id)
        parsed_candidates.append({
            "id": candidate_id,
            "filename": filename,
            "parsed": parsed,
            "search_score": search_score
        })
        print(f"    Parsed: {parsed.name} ({filename})")
    
    # Step 5: Compute multi-signal scores
    print("\n[STEP 5] Computing multi-signal scores...")
    scored_candidates = []
    
    for c in parsed_candidates:
        parsed = c["parsed"]
        
        # Signal 1: Semantic similarity
        semantic = compute_semantic_score(parsed_jd.summary, parsed.summary)
        
        # Signal 2: Skill match
        skill = compute_skill_match_score(
            parsed_jd.must_have_skills,
            parsed_jd.nice_to_have_skills,
            parsed.skills
        )
        
        # Signal 3: Experience fit
        experience = compute_experience_score(
            parsed.experience_years,
            parsed_jd.min_experience_years,
            parsed_jd.max_experience_years
        )
        
        # Signal 4: Project relevance
        project_text = " ".join([p.name + " " + p.description for p in parsed.projects])
        project = compute_semantic_score(parsed_jd.summary, project_text) if project_text.strip() else 0.5
        
        # Aggregate
        aggregate = compute_aggregate_score(semantic, skill, experience, project)
        
        signals = {
            "semantic": semantic,
            "skill": skill,
            "experience": experience,
            "project": project,
            "aggregate": aggregate
        }
        
        c["signals"] = signals
        c["aggregate"] = aggregate
        scored_candidates.append(c)
        
        print(f"    {parsed.name}: semantic={semantic:.2f}, skill={skill:.2f}, exp={experience:.2f}, project={project:.2f} -> aggregate={aggregate:.2f}")
    
    # Step 6: LLM evaluation
    print("\n[STEP 6] LLM evaluation of each candidate...")
    
    for c in scored_candidates:
        evaluation = llm_evaluator_chain.evaluate(parsed_jd, c["parsed"], c["signals"])
        c["evaluation"] = evaluation
        print(f"    {c['parsed'].name}: {evaluation.fit_summary[:80]}...")
    
    # Step 7: Sort by aggregate score
    print("\n[STEP 7] Sorting by aggregate score...")
    scored_candidates.sort(key=lambda x: x["aggregate"], reverse=True)
    
    for i, c in enumerate(scored_candidates):
        print(f"    {i+1}. {c['parsed'].name} ({c['aggregate']:.3f})")
    
    # Step 8: LLM reranking
    print("\n[STEP 8] LLM reranking for final order...")
    
    rerank_input = [
        RankedCandidate(
            candidate_id=c["id"],
            name=c["parsed"].name,
            rank=0,
            final_score=c["aggregate"],
            signals=ScoringSignals(**c["signals"]),
            evaluation=c["evaluation"],
            reason=""
        )
        for c in scored_candidates
    ]
    
    reranked = reranker_chain.rerank(parsed_jd, rerank_input)
    
    # Step 9: Final results
    print("\n" + "=" * 60)
    print("FINAL RANKINGS")
    print("=" * 60)
    
    for r in reranked:
        c = next(x for x in scored_candidates if x["id"] == r.candidate_id)
        print(f"\nRank {r.rank}: {c['parsed'].name}")
        print(f"  File: {c['filename']}")
        print(f"  Score: {c['aggregate']:.3f}")
        print(f"  Signals: semantic={c['signals']['semantic']:.2f}, skill={c['signals']['skill']:.2f}, exp={c['signals']['experience']:.2f}")
        print(f"  Reason: {r.reason}")
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

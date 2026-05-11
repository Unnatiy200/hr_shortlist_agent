from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

os.makedirs("data/sample_resumes", exist_ok=True)

resumes = [
    {
        "filename": "priya_sharma.pdf",
        "content": [
            "PRIYA SHARMA",
            "Email: [EMAIL] | Phone: [PHONE]",
            "",
            "SUMMARY",
            "Senior ML Engineer with 7 years at Google Brain and Spotify.",
            "Expert in PyTorch, LLM fine-tuning, RAG pipelines, vector databases.",
            "Led 3-person team building recommendation system for 100M users.",
            "",
            "EXPERIENCE",
            "Google Brain - Senior ML Engineer (2020-2025) 5 years",
            "- Built LLM fine-tuning pipelines using PyTorch and DeepSpeed",
            "- Deployed RAG systems using Pinecone and LangChain",
            "- Managed Kubernetes clusters on AWS SageMaker",
            "",
            "Spotify - ML Engineer (2018-2020) 2 years",
            "- Built music recommendation models",
            "- Deployed Docker containers on GCP Vertex AI",
            "",
            "EDUCATION",
            "PhD Computer Science - Stanford University (2018)",
            "",
            "SKILLS",
            "Python, PyTorch, TensorFlow, LLMOps, RAG, Pinecone,",
            "Docker, Kubernetes, AWS SageMaker, GCP Vertex AI, MLflow",
            "",
            "PUBLICATIONS",
            "4 papers published at NeurIPS and ICML",
            "Open source contributor - 2000+ GitHub stars"
        ]
    },
    {
        "filename": "carlos_mendez.pdf",
        "content": [
            "CARLOS MENDEZ",
            "Email: [EMAIL] | Phone: [PHONE]",
            "",
            "SUMMARY",
            "ML Engineer with 4 years experience in NLP and data science.",
            "Strong Python skills, basic PyTorch, good communicator.",
            "",
            "EXPERIENCE",
            "TechStartup - ML Engineer (2021-2025) 4 years",
            "- Built NLP sentiment analysis models using Scikit-learn",
            "- Some exposure to Docker for containerisation",
            "- Worked on basic recommendation systems",
            "",
            "EDUCATION",
            "Bachelor of Mathematics - University of Madrid (2021)",
            "",
            "SKILLS",
            "Python, Scikit-learn, PyTorch (basic), Docker, SQL, Pandas",
            "",
            "PROJECTS",
            "Sentiment classifier open source - 120 GitHub stars",
            "Customer churn prediction model for e-commerce client"
        ]
    },
    {
        "filename": "aisha_okonkwo.pdf",
        "content": [
            "AISHA OKONKWO",
            "Email: [EMAIL] | Phone: [PHONE]",
            "",
            "SUMMARY",
            "Data Scientist with 6 years experience. Recently upskilled in LLMOps.",
            "Deployed 2 RAG systems at current employer. Top 3% Kaggle.",
            "",
            "EXPERIENCE",
            "DataCorp - Senior Data Scientist (2019-2025) 6 years",
            "- Deployed 2 RAG systems using LangChain and Pinecone",
            "- Built ML pipelines using Scikit-learn and Pandas",
            "- Presented findings at PyData London 2023",
            "",
            "EDUCATION",
            "MSc Statistics - University College London (2019)",
            "",
            "SKILLS",
            "Python, Pandas, Scikit-learn, LangChain, Pinecone, SQL,",
            "Power BI, Tableau, basic Docker",
            "",
            "ACHIEVEMENTS",
            "Kaggle contributor - top 3% global ranking",
            "Speaker at PyData London 2023"
        ]
    },
    {
        "filename": "james_whitfield.pdf",
        "content": [
            "JAMES WHITFIELD",
            "Email: [EMAIL] | Phone: [PHONE]",
            "",
            "SUMMARY",
            "Backend Engineer transitioning to ML.",
            "3 years Python API development, 1 year studying ML.",
            "No production ML deployment experience yet.",
            "",
            "EXPERIENCE",
            "WebAgency - Backend Developer (2022-2025) 3 years",
            "- Built REST APIs using FastAPI and Django",
            "- Deployed applications on AWS EC2 and Docker",
            "- Strong on system design and databases",
            "",
            "EDUCATION",
            "BSc Computer Science - University of Leeds (2022)",
            "Coursera ML Specialisation - Andrew Ng (2024)",
            "",
            "SKILLS",
            "Python, FastAPI, Django, Docker, AWS, PostgreSQL, Redis",
            "ML: basic Scikit-learn, following PyTorch tutorials",
            "",
            "PROJECTS",
            "Technical blog about ML concepts - 500 monthly readers"
        ]
    },
    {
        "filename": "mei_ling_chen.pdf",
        "content": [
            "MEI-LING CHEN",
            "Email: [EMAIL] | Phone: [PHONE]",
            "",
            "SUMMARY",
            "ML Research Engineer with 5 years experience.",
            "PyTorch expert. Co-authored DeepSpeed paper. PhD MIT.",
            "8 published papers. Strong distributed training background.",
            "",
            "EXPERIENCE",
            "AI Research Lab - ML Research Engineer (2020-2025) 5 years",
            "- Co-authored DeepSpeed distributed training paper",
            "- Implemented FSDP and model parallelism for LLM training",
            "- Deployed fine-tuned models on GCP Vertex AI",
            "",
            "EDUCATION",
            "PhD Computer Science - MIT (2020)",
            "",
            "SKILLS",
            "Python, PyTorch, DeepSpeed, FSDP, GCP Vertex AI,",
            "Distributed training, CUDA, LLM fine-tuning, Hugging Face",
            "",
            "PUBLICATIONS",
            "8 papers published at NeurIPS, ICML, ICLR",
            "Co-author of DeepSpeed paper - 500+ citations"
        ]
    }
]

for resume in resumes:
    filepath = f"data/sample_resumes/{resume['filename']}"
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    y = height - 50

    for line in resume["content"]:
        if y < 50:
            c.showPage()
            y = height - 50

        if line == resume["content"][0]:
            c.setFont("Helvetica-Bold", 16)
        elif line in ["SUMMARY", "EXPERIENCE", "EDUCATION",
                      "SKILLS", "PROJECTS", "PUBLICATIONS", "ACHIEVEMENTS"]:
            c.setFont("Helvetica-Bold", 12)
            y -= 10
        elif line == "":
            y -= 8
            continue
        else:
            c.setFont("Helvetica", 10)

        c.drawString(50, y, line)
        y -= 18

    c.save()
    print(f"Created {filepath}")

print("\nAll 5 sample resumes created in data/sample_resumes/")
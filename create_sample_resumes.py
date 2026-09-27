"""
Generates sample resumes in TXT, DOCX, and PDF formats for testing and demo.
"""
import os
from docx import Document
from pypdf import PdfWriter

SAMPLE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sample_resumes")
os.makedirs(SAMPLE_DIR, exist_ok=True)

# 1. Alice - Python Backend Engineer (TXT)
alice_txt = """Alice Walker
Email: alice.walker@email.com
Phone: +1-555-019-2834
LinkedIn: linkedin.com/in/alicewalker-dev

SUMMARY:
Results-driven Senior Backend Developer with 4 years of experience building scalable RESTful web APIs and microservices using Python, Flask, and PostgreSQL. Proficient with Docker, Git, CI/CD pipelines, and cloud deployment on AWS.

TECHNICAL SKILLS:
- Languages: Python, SQL, C++, Bash
- Frameworks & Libraries: Flask, FastAPI, SQLAlchemy, PyTest, NumPy, Pandas
- Databases: PostgreSQL, MySQL, Redis, SQLite
- Cloud & Tools: Docker, Git, GitHub Actions, AWS, Linux, NGINX

PROFESSIONAL EXPERIENCE:
Software Engineer | DataCore Systems | 2022 - Present
- Architected and implemented high-throughput REST APIs in Python using Flask and SQLAlchemy, handling 2M+ daily requests.
- Integrated Redis caching layers, reducing database read latency by 45%.
- Implemented comprehensive automated unit and integration tests using pytest, achieving 92% code coverage.
- Configured automated CI/CD pipelines via GitHub Actions and containerized microservices using Docker.

Junior Backend Developer | CloudVibe Inc. | 2020 - 2022
- Developed database migration scripts and optimized complex SQL queries in PostgreSQL.
- Built authentication services using JWT and secure password hashing.
- Collaborated in an agile scrum team to deliver production backend features on two-week sprint cycles.

EDUCATION:
B.Tech in Computer Science and Engineering | State University (2016 - 2020)
"""

with open(os.path.join(SAMPLE_DIR, "alice_backend_developer.txt"), "w", encoding="utf-8") as f:
    f.write(alice_txt)

# 2. Bob - Frontend Developer (TXT)
bob_txt = """Bob Martinez
Email: bob.martinez@email.com
Phone: +1-555-014-9922

SUMMARY:
Creative Frontend Engineer specializing in responsive web applications, interactive user interfaces, and state management using JavaScript, TypeScript, React, and Next.js.

TECHNICAL SKILLS:
- Languages: JavaScript, TypeScript, HTML5, CSS3
- Frameworks: React, Next.js, Vue.js, Tailwind CSS, Bootstrap
- Tools: Git, Webpack, Jest, Figma

PROFESSIONAL EXPERIENCE:
Frontend Developer | PixelCraft Studio | 2022 - Present
- Designed and built responsive web applications using React, Next.js, and Tailwind CSS.
- Improved frontend Core Web Vitals and LCP scores by 35%.
- Integrated REST APIs with client-side state management.

EDUCATION:
B.S. in Information Technology | City College (2018 - 2022)
"""

with open(os.path.join(SAMPLE_DIR, "bob_frontend_developer.txt"), "w", encoding="utf-8") as f:
    f.write(bob_txt)

# 3. Carol - Machine Learning Engineer (DOCX)
doc = Document()
doc.add_heading("Carol Danvers", level=1)
doc.add_paragraph("Email: carol.danvers@email.com | Phone: +1-555-832-1102")
doc.add_heading("Professional Summary", level=2)
doc.add_paragraph("Machine Learning and Data Science Engineer with 3+ years of expertise designing predictive models, natural language processing pipelines, and deep neural networks in Python.")
doc.add_heading("Technical Skills", level=2)
doc.add_paragraph("Python, Machine Learning, Deep Learning, NLP, PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, SQL, Docker, Git")
doc.add_heading("Experience", level=2)
doc.add_paragraph("AI Engineer at Cortex Analytics (2022 - Present): Trained NLP transformers and sentence embedding models. Built automated data pipelines using Pandas and Scikit-Learn. Deployed models via FastAPI and Docker.")
doc.add_heading("Education", level=2)
doc.add_paragraph("M.S. in Artificial Intelligence, Tech University (2020 - 2022)")
doc.save(os.path.join(SAMPLE_DIR, "carol_ml_engineer.docx"))

# 4. David - Full Stack Developer (PDF)
# Generate a valid PDF using minimal PDF header/stream structure
pdf_content = """%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 420 >>
stream
BT
/F1 18 Tf
50 720 Td
(David Kumar - Full Stack Developer) Tj
/F1 11 Tf
0 -30 Td
(Email: david.kumar@techmail.com | Phone: +1-555-481-9032) Tj
0 -25 Td
(Skills: Python, Flask, SQL, JavaScript, React, REST API, Git, Docker) Tj
0 -25 Td
(Experience: 3 years building web apps with Flask backend and React frontend.) Tj
0 -20 Td
(Developed scalable REST APIs, optimized SQL queries, and deployed on cloud.) Tj
0 -25 Td
(Education: B.Tech Computer Science, 2021) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000229 00000 n 
0000000701 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
770
%%EOF
"""

with open(os.path.join(SAMPLE_DIR, "david_fullstack_developer.pdf"), "wb") as f:
    f.write(pdf_content.encode("ascii"))

print("Sample resumes successfully generated in:", SAMPLE_DIR)

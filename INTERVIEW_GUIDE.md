# SDE Interview Preparation Guide: AI Resume Screening Platform

This guide is specifically tailored for a **B.Tech Computer Science / Software Engineering student** presenting this project in Software Developer (SDE-1 / SWE) interviews at top tech companies.

---

## 📌 Section 1: Executive Pitches

### A. 30-Second Elevator Pitch
> *"I built an **AI-Powered Resume Screening & Job Matching Platform** that solves the manual bottleneck recruiters face when reviewing hundreds of resumes. It ingests resumes in PDF, DOCX, and TXT formats, extracts structured text and candidate contact details, and evaluates applicants against job postings using a multi-layered NLP pipeline: **TF-IDF for keyword relevance**, **Sentence Transformers for contextual semantic similarity**, and a **custom skill taxonomy engine** for exact stack coverage. The system produces an explainable, weighted match score from 0 to 100%, highlights domain strengths and missing skills, and provides recruiters with a dynamic dashboard to filter, sort, and rank top applicants."*

---

### B. 2-Minute Detailed Project Walkthrough
> *"When hiring for technical roles, recruiters often receive hundreds of resumes per job posting. Traditional Applicant Tracking Systems (ATS) rely either on naive keyword matching—which penalizes candidates who use synonyms—or opaque AI models that output a score without explanation.*
> 
> *To address both problems, I developed this full-stack platform using **Python, Flask, SQLite, and vanilla HTML/CSS/JavaScript**. Here is how it functions end-to-end:*
>
> 1. *A recruiter logs in securely via a JWT-authenticated session and creates a job posting specifying required skills, experience, and job description.*
> 2. *Candidates or recruiters upload resumes in PDF, DOCX, or TXT format. The backend validates file extensions and sizes, saves them securely, and parses raw text using `pypdf` and `python-docx` while capturing contact metadata.*
> 3. *The text is preprocessed: technical tokens like C++, C#, .NET, and Node.js are protected from destructive punctuation stripping.*
> 4. *The matching pipeline runs in three layers:*
>    - *First, **TF-IDF with Cosine Similarity** checks keyword alignment and terminology density.*
>    - *Second, **Sentence Transformers (`all-MiniLM-L6-v2`)** generates 384-dimensional dense semantic embeddings to detect conceptual overlap even when wording differs—like matching 'predictive modeling' with 'machine learning'.*
>    - *Third, our **Skill Matcher** verifies required and preferred technical stacks, tracking matched and missing skills.*
> 5. *A **Candidate Scorer** combines these three sub-scores using a configurable formula (30% TF-IDF, 40% Semantic, 30% Skill Match).*
> 6. *Importantly, the system is **explainable**: it does not just output an 82% score; it displays the exact points contributed by each layer, identifies domain strengths like Backend or Cloud, and warns about missing skills.*
> 7. *Recruiters can filter candidates by minimum score, search by skill, and rank candidates instantly on a clean, responsive dashboard.*
> 
> *The entire codebase is structured using the Service-Repository pattern with 30 automated tests in `pytest`."*

---

## 🏛️ Section 2: Deep-Dive Architecture & Core Concepts

### C. Complete Architecture Explanation
The application adopts a **Layered Architecture (Client-Server / 3-Tier)**:
1. **Presentation Layer (Frontend)**: Pure HTML5, CSS3, and ES6 JavaScript (`fetch` API). It manages state client-side, renders UI dynamically, and stores JWT tokens in `localStorage`.
2. **API & Routing Layer (Flask Blueprints)**: Exposes clean RESTful endpoints divided into modular blueprints (`auth_bp`, `jobs_bp`, `resumes_bp`, `candidates_bp`).
3. **Validation & Security Layer**: Validates email formats, passwords, file MIME types, payload structures, and verifies JWT tokens.
4. **Service Layer (Business & NLP Logic)**: Decoupled Python classes (`ResumeParser`, `TextPreprocessor`, `TFIDFMatcher`, `SemanticMatcher`, `SkillMatcher`, `CandidateScorer`).
5. **Persistence Layer (SQLite + SQLAlchemy ORM)**: Manages relational data with foreign key integrity and automated migrations via `db.create_all()`.

---

### D. How Frontend Communicates with Backend
- Communication is **stateless over HTTP/HTTPS** using JSON format.
- When an action occurs (e.g., clicking *"Post Job"*), JavaScript executes `authFetch()`.
- If the endpoint requires authentication, `authFetch()` automatically injects:
  ```http
  Authorization: Bearer <jwt_token>
  Content-Type: application/json
  ```
- File uploads use standard `multipart/form-data` with `FormData()` to stream binary PDF/DOCX bytes directly to `/api/resumes/upload`.

---

### E. What REST API Means
**REST (Representational State Transfer)** is an architectural style for networked applications based on six constraints:
1. **Client-Server Separation**: Frontend and backend evolve independently.
2. **Statelessness**: Every request contains all information needed to process it; the server stores no session state between calls.
3. **Cacheability**: Responses explicitly declare whether they can be cached.
4. **Uniform Interface**: Standard HTTP verbs (`GET` for reading, `POST` for creating, `PUT` for updating, `DELETE` for removing) with uniform resource identifiers (`/api/jobs/<id>`).
5. **Layered System**: The client doesn't need to know if it communicates directly with the app server or an intermediate proxy.

---

### F. What Flask Does
Flask is a lightweight **WSGI (Web Server Gateway Interface)** Python framework.
- It receives HTTP requests from the OS network socket, parses HTTP headers and bodies into the `request` context, matches the URL against registered routes, calls the route handler function, and packages the return value into an HTTP response string with status codes and headers.

---

### G. API Endpoints Table

| Method | Endpoint | Purpose | Request Body / Params | Status Code |
|---|---|---|---|---|
| `POST` | `/api/auth/register` | Register new recruiter | `name`, `email`, `password` | `201 Created` |
| `POST` | `/api/auth/login` | Authenticate recruiter & get JWT | `email`, `password` | `200 OK` |
| `GET` | `/api/auth/me` | Fetch authenticated recruiter profile | Requires Bearer Token | `200 OK` |
| `POST` | `/api/jobs` | Create a job posting | `title`, `description`, `required_skills` | `201 Created` |
| `GET` | `/api/jobs` | List all job postings | None | `200 OK` |
| `GET` | `/api/jobs/<id>` | Get job details | `job_id` | `200 OK` / `404` |
| `PUT` | `/api/jobs/<id>` | Update job posting | `title`, `description`, etc. | `200 OK` |
| `DELETE` | `/api/jobs/<id>` | Delete job and its matches | `job_id` | `200 OK` |
| `POST` | `/api/resumes/upload` | Upload resume file | `file` (multipart), `job_id` (opt) | `201 Created` |
| `GET` | `/api/resumes` | List uploaded resumes | None | `200 OK` |
| `GET` | `/api/resumes/<id>` | Get resume + extracted text | `resume_id` | `200 OK` |
| `DELETE` | `/api/resumes/<id>` | Delete resume & local file | `resume_id` | `200 OK` |
| `POST` | `/api/match/<job_id>/<resume_id>` | Evaluate resume against job | `job_id`, `resume_id` | `200 OK` |
| `POST` | `/api/match/quick` | Live sandbox match on arbitrary text | `job_description`, `resume_text` | `200 OK` |
| `POST` | `/api/jobs/<id>/match-all` | Batch evaluate all resumes for job | `job_id` | `200 OK` |
| `GET` | `/api/jobs/<id>/candidates` | Get ranked candidates list | `?min_score=&skill=&sort=` | `200 OK` |
| `GET` | `/api/jobs/<id>/export` | Export candidates ranking to CSV | `job_id` | `200 OK` (CSV stream) |
| `GET` | `/api/match/<match_id>` | Get explainable match report | `match_id` | `200 OK` |
| `GET` | `/api/dashboard/stats` | Platform statistics & top talent | None | `200 OK` |

---

### H. How Resume Upload Works
1. Frontend sends a `POST` request with `multipart/form-data`.
2. Flask checks `if "file" not in request.files` and ensures non-empty filename.
3. Extension whitelist validation ensures only `.pdf`, `.docx`, and `.txt` are accepted.
4. `secure_filename()` sanitizes the filename to prevent directory traversal attacks (`../../etc/passwd`).
5. A UUID prefix is prepended (`uuid4().hex[:8] + "_" + filename`) to prevent filename collisions.
6. The file is saved to the `uploads/` directory.
7. Text is extracted immediately via `ResumeParser`. If parsing fails, the physical file is deleted to avoid orphaned clutter.

---

### I. How PDF and DOCX Parsing Works
- **PDF Extraction**: Uses `pypdf.PdfReader`. A PDF file is a structured tree of objects (Catalog, Pages, Content Streams). `pypdf` navigates the object tree, parses Content Streams (commands like `BT` Begin Text, `Tj` Show Text, `ET` End Text), decompresses Flate-encoded font streams, and outputs Unicode text.
- **DOCX Extraction**: A `.docx` file is actually a zipped archive of XML files. `python-docx` unpacks `word/document.xml`, parses `<w:p>` (paragraphs) and `<w:r>` (runs of text), as well as `<w:tbl>` (tables) so tabular experience data is not lost.
- **TXT Extraction**: Tries UTF-8 decoding with Latin-1/CP1252 fallbacks to prevent character encoding crashes.

---

### J. How TF-IDF Works
TF-IDF (**Term Frequency - Inverse Document Frequency**) reflects how important a word is to a document within a corpus:
$$\text{TF}(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}$$
$$\text{IDF}(t, D) = \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
- If a word like *"Python"* appears frequently in the resume, its **TF is high**.
- Common words like *"the"*, *"with"*, *"experience"* appear across all documents, so their **IDF is low**.
- Rare technical keywords get **high TF-IDF weights**.

---

### K. How Cosine Similarity Works
Cosine similarity measures the cosine of the angle between two multi-dimensional vectors in a vector space:
$$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|} = \frac{\sum_{i=1}^n u_i v_i}{\sqrt{\sum_{i=1}^n u_i^2} \sqrt{\sum_{i=1}^n v_i^2}}$$
- When two documents share identical word distributions, $\theta = 0^\circ \implies \cos(0^\circ) = 1.0$ (100% match).
- When they share no words, $\theta = 90^\circ \implies \cos(90^\circ) = 0.0$ (0% match).
- **Advantage over Euclidean distance**: Cosine similarity is **length-invariant**. A 3-page resume and a 1-page resume discussing the same topics will yield high similarity, whereas Euclidean distance would penalize length differences.

---

### L. Why Sentence Transformers are Used
Keyword matching alone fails when candidates describe skills using synonyms:
- Job: *"Experience in machine learning and predictive modeling."*
- Resume: *"Trained deep neural networks and classification algorithms in PyTorch."*
- **TF-IDF score would be very low** because exact keywords don't match.
- **Sentence Transformers (`all-MiniLM-L6-v2`)** maps sentences into a dense 384-dimensional continuous vector space trained on over 1 billion sentence pairs using Siamese network architectures. Because the words appear in similar contexts, their dense vector embeddings point in nearly the same direction, yielding high cosine similarity.

---

### M. How Skill Matching Works
1. We maintain a curated catalog of programming languages, frameworks, cloud tools, and databases.
2. We map common aliases: `k8s` $\rightarrow$ `Kubernetes`, `react.js` $\rightarrow$ `React`, `postgres` $\rightarrow$ `PostgreSQL`.
3. Skills are extracted from both the job posting and the resume using word-boundary regular expressions (`\b`).
4. Set operations compute:
   $$\text{Matched Skills} = \text{Required Skills} \cap \text{Resume Skills}$$
   $$\text{Missing Skills} = \text{Required Skills} \setminus \text{Resume Skills}$$
5. The ratio $\frac{|\text{Matched}|}{|\text{Required}|}$ determines the skill score, with a small bonus for matched preferred/nice-to-have skills.

---

### N. How Weighted Scoring Works
The candidate score combines three complementary dimensions:
$$\text{Overall Score} = (0.30 \times \text{TF-IDF}) + (0.40 \times \text{Semantic}) + (0.30 \times \text{Skill}) \times 100$$
- **TF-IDF (30%)**: Guarantees keyword accuracy and specific tool mentions.
- **Semantic (40%)**: Assesses overall experience relevance and conceptual domain depth.
- **Skill Match (30%)**: Enforces hard requirements (e.g., candidate must know SQL).
- Weights are normalized and fully configurable in `config.py`.

---

### O. How Candidate Ranking Works
1. For a given job ID, the system queries all evaluations in `match_results`.
2. Results are ordered: `ORDER BY overall_score DESC`.
3. Filter parameters (`min_score`, `skill`, `search`) are applied sequentially.
4. Ranks ($1, 2, 3, \dots, N$) are assigned to the filtered list and returned as structured JSON.

---

### P. How Database Works & Q. Why SQLite Was Selected
- **SQLite** is a serverless, self-contained, transactional SQL database engine that stores data in a single cross-platform disk file (`database.db`).
- **Why selected**:
  1. **Zero Configuration**: No separate database daemon (like PostgreSQL or MySQL) required, making the project immediately cloneable and executable by any interviewer or evaluator.
  2. **ACID Compliant**: Full transactional integrity for user creations and resume updates.
  3. **Abstraction via SQLAlchemy**: Because we used SQLAlchemy ORM, switching to PostgreSQL or MySQL in production requires changing **only one line** in `config.py` (`DATABASE_URL = "postgresql://user:pass@host/dbname"`).

---

### R. Authentication Flow
```
Client (Browser)                 Server (Flask)
       |                               |
       |  POST /api/auth/login         |
       |  {email, password}            |
       |------------------------------>|
       |                               | 1. Query User by email
       |                               | 2. check_password_hash()
       |                               | 3. Create JWT with payload:
       |                               |    {sub: user_id, exp: +24h}
       |  200 OK {token, user}         |
       |<------------------------------|
       |                               |
       | Store token in localStorage   |
       |                               |
       |  GET /api/auth/me             |
       |  Header: Bearer <token>       |
       |------------------------------>|
       |                               | 4. Decode & verify JWT
       |                               | 5. Return user profile
       |  200 OK {user}                |
       |<------------------------------|
```

---

### S. Error Handling & T. Input Validation
- **Custom Error Handlers**: Flask returns standardized JSON objects on HTTP `400`, `401`, `404`, `413`, and `500` rather than default HTML error pages.
- **Defensive Validation**:
  - `is_valid_email`: Regex checking user emails.
  - `validate_password_strength`: Minimum 6 characters.
  - `validate_job_input`: Title non-empty, description $\ge 20$ chars, at least one skill.
  - `MAX_CONTENT_LENGTH`: Rejects files $>10\text{ MB}$ with HTTP `413`.
  - Extension Whitelist: Only `.pdf`, `.docx`, `.txt`.

---

### U. Automated Testing Strategy
- Tests are written in **`pytest`** using Flask's `test_client`.
- Runs against an **in-memory SQLite database** (`sqlite:///:memory:`) so unit tests never pollute production data.
- Covers:
  - User registration, duplicate email rejection, weak password handling.
  - Login success and authentication failure.
  - Job CRUD operations and input boundary validation.
  - Resume parser across PDF, DOCX, TXT, corrupted, and empty files.
  - NLP algorithms (TF-IDF vector bounds, semantic cosine similarity, skill taxonomy).
  - End-to-end API workflows (upload $\rightarrow$ match $\rightarrow$ rank $\rightarrow$ filter).

---

### V. Challenges Faced & How They Were Solved
1. **Punctuation Stripping vs. Technical Vocabulary**:
   - *Challenge*: Standard text cleaners remove all punctuation, converting `C++` into `C`, `C#` into `C`, and `.NET` into `NET`.
   - *Solution*: Implemented a dictionary protection step in `text_preprocessor.py` that maps `C++` $\rightarrow$ `cpp_token` before cleaning, and restores it afterward.
2. **Cold-Start Model Download Latency**:
   - *Challenge*: Sentence Transformers download ~90MB weights from HuggingFace on first run, which can stall automated test suites or offline deployments.
   - *Solution*: Designed a lazy-loaded architecture with a fallback sub-word character n-gram dense approximation so tests and offline executions run instantly in 3 seconds.
3. **Regex in Character Classes**:
   - *Challenge*: Putting keywords like `resume` inside regex bracket character classes `[resume]` matches every individual letter.
   - *Solution*: Replaced with non-capturing groups `(?:resume|cv|curriculum)`.

---

### W. Future Architectural Improvements
1. **Asynchronous Task Queue (Celery + Redis)**: Process large batches of 500+ resumes asynchronously in the background.
2. **OCR Integration (Tesseract / EasyOCR)**: Parse image-based and scanned PDFs.
3. **Vector Database (Qdrant / Milvus / ChromaDB)**: Pre-index millions of resume embeddings for millisecond nearest-neighbor search.
4. **LLM Explanations**: Use Gemini API to generate personalized feedback emails for candidates outlining areas of improvement.

---

## 🎯 Section 3: 40 SDE Interview Questions & Model Answers

### 🟢 Beginner Questions (1 - 10)

#### Q1. What is the difference between a GET and a POST request in your application?
- **Answer**: `GET` is used to retrieve data from the server without modifying server state (it is idempotent and safe), such as `GET /api/jobs` or `GET /api/jobs/1/candidates`. `POST` is used to submit data to the server to create a resource or trigger an action (it is non-idempotent), such as `POST /api/jobs` to create a job or `POST /api/resumes/upload` to upload a file.
- **Follow-up Question**: *Why shouldn't sensitive data like passwords be sent in GET requests?* (Because GET parameters are appended to the URL query string, where they get logged in browser history, proxy logs, and server access logs in plaintext).

#### Q2. Why did you use Flask instead of Django for this project?
- **Answer**: Flask is a lightweight micro-framework that provides only the core essentials (routing, request handling, templating) without enforcing an opinionated directory structure, ORM, or admin panel. This makes it ideal for building lightweight REST APIs where we want complete control over the NLP service pipeline and architecture. Django includes a lot of built-in boilerplate that wasn't necessary for this focused service.
- **Follow-up Question**: *When would you choose Django over Flask?* (When building large enterprise applications requiring built-in ORM migrations, an out-of-the-box admin dashboard, complex user permission groups, and built-in CSRF/security middleware).

#### Q3. What is an API and what does JSON stand for?
- **Answer**: API stands for **Application Programming Interface**—it defines a contract of rules, endpoints, and data formats through which two software applications communicate. JSON stands for **JavaScript Object Notation**, a lightweight, human-readable text format for data interchange based on key-value pairs and arrays.
- **Follow-up Question**: *Why is JSON preferred over XML in modern REST APIs?* (JSON is less verbose, lighter to transmit over the network, and natively parsed by JavaScript into objects without complex DOM parsers).

#### Q4. Why did you hash passwords instead of storing them in plain text?
- **Answer**: Plaintext passwords in a database represent a catastrophic vulnerability; if the database is leaked or accessed by an unauthorized party, all user accounts are compromised across all services where users reuse passwords. We use **Werkzeug's salted password hashing**, which runs a one-way cryptographic hash function combined with a unique random salt, ensuring the original password cannot be recovered even if the hash table is compromised.
- **Follow-up Question**: *What is the purpose of the salt in password hashing?* (Salt prevents attackers from using precomputed lookup tables, known as Rainbow Tables, to crack common passwords).

#### Q5. What is SQLite and where is the data physically stored?
- **Answer**: SQLite is a self-contained, serverless, zero-configuration SQL database engine. Unlike client-server databases like MySQL, SQLite runs in-process inside the Python runtime and stores all tables, indices, and records inside a single file on disk located at `instance/database.db`.
- **Follow-up Question**: *Can multiple processes write to SQLite simultaneously?* (SQLite locks the entire database file during writes, so while multiple processes can read simultaneously, concurrent writes can cause `database is locked` errors under high concurrency).

#### Q6. What HTTP status code is returned when a requested job does not exist?
- **Answer**: `404 Not Found`. In our API, if `db.session.get(Job, job_id)` returns `None`, the route immediately returns `jsonify({"success": False, "error": "Job not found"}), 404`.
- **Follow-up Question**: *What is the difference between a 401 Unauthorized and a 403 Forbidden status code?* (401 means authentication is required and has failed or not been provided. 403 means the server understands who the user is, but the user does not have permission to access that specific resource).

#### Q7. What is the role of `requirements.txt` in a Python project?
- **Answer**: It lists all external third-party packages and their specific versions required to run the application. It allows another developer to recreate the exact execution environment by running `pip install -r requirements.txt`.
- **Follow-up Question**: *Why is version pinning (e.g. `Flask>=3.0.0`) recommended?* (To prevent breaking changes in newer upstream package releases from crashing your existing production codebase).

#### Q8. What does `db.session.commit()` and `db.session.rollback()` do?
- **Answer**: In SQLAlchemy, `db.session` represents a database transaction unit-of-work. When we add or modify entities, changes are staged in memory. `db.session.commit()` permanently writes all staged operations to disk within an atomic database transaction. If an exception occurs, `db.session.rollback()` aborts the transaction, reverting any partial changes to preserve database consistency.
- **Follow-up Question**: *What is the ACID principle in databases?* (Atomicity, Consistency, Isolation, Durability).

#### Q9. How do you handle file uploads in Flask?
- **Answer**: When the client sends an HTTP `POST` request with `Content-Type: multipart/form-data`, Flask parses the binary parts and exposes them via `request.files`. We retrieve the uploaded file object using `request.files['file']`, validate its filename and extension, sanitize the name with `secure_filename()`, and write it to disk using `file.save(destination_path)`.
- **Follow-up Question**: *What prevents a malicious user from uploading an executable file like `malware.exe`?* (Our `validate_file_extension()` function checks the file extension against a strict whitelist of `{'pdf', 'docx', 'txt'}` and rejects everything else with HTTP 400).

#### Q10. What is CORS and why might it occur?
- **Answer**: CORS stands for **Cross-Origin Resource Sharing**. It is a browser security mechanism that blocks web pages on one origin (domain, protocol, or port) from making requests to a different origin unless the server explicitly sends `Access-Control-Allow-Origin` headers. In our project, because Flask serves both the static frontend and the REST API from the same port (5000), same-origin policy applies and CORS issues do not arise.
- **Follow-up Question**: *How would you enable CORS if the frontend was hosted on port 3000 (React) and the backend on port 5000?* (By using the `flask-cors` package and calling `CORS(app)`).

---

### 🟡 Intermediate Questions (11 - 25)

#### Q11. Explain how TF-IDF works mathematically and conceptually.
- **Answer**: TF-IDF evaluates word importance by multiplying Term Frequency by Inverse Document Frequency.
  - **TF** measures how often term $t$ appears in document $d$: $\frac{\text{count}(t, d)}{\text{total words in } d}$.
  - **IDF** measures the rarity of the term across all documents: $\log(\frac{1 + N}{1 + \text{df}(t)}) + 1$.
  - Common words like *"and"* or *"with"* have high TF but low IDF because they appear in every document, resulting in a low score. Specialized technical keywords like *"Kubernetes"* or *"FastAPI"* appear frequently in relevant resumes but rarely in others, yielding high TF-IDF weights.
- **Follow-up Question**: *Why did you use n-grams in TF-IDF?* (Using `ngram_range=(1, 2)` allows us to capture two-word phrases like *"machine learning"* or *"rest api"* as single semantic tokens rather than isolating the individual words *"machine"* and *"learning"*).

#### Q12. Why did you use Cosine Similarity instead of Euclidean Distance?
- **Answer**: Euclidean distance measures the straight-line geometric distance between two vector coordinates. If a candidate writes a comprehensive 3-page resume covering Python and Flask, their term frequencies will be higher than in a concise 1-page resume covering the same skills. Euclidean distance would treat them as distant. Cosine similarity evaluates the **angle** between the vectors ($\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|\|\mathbf{v}\|}$), which normalizes for document length and measures topical orientation rather than document length.
- **Follow-up Question**: *Can cosine similarity produce negative values in text processing?* (Because term frequencies in TF-IDF vectors are non-negative, document vectors always lie in the first quadrant, meaning cosine similarity strictly ranges between 0.0 and 1.0).

#### Q13. What is a JWT and how does stateless authentication work?
- **Answer**: A JWT (**JSON Web Token**) is a cryptographically signed compact string consisting of three parts separated by dots: **Header**, **Payload**, and **Signature**. When a user logs in, the server signs a payload containing the user's ID and token expiration time using a secret key (`jwt.encode`). The client stores this token and sends it in the `Authorization: Bearer <token>` header on subsequent requests. The server validates the signature mathematically using the same secret key without needing to query a session table in a database, making authentication stateless and scalable.
- **Follow-up Question**: *What is the drawback of JWTs compared to server-side sessions?* (JWTs cannot be easily revoked before their expiration time unless you maintain a token blocklist in a cache like Redis).

#### Q14. How does your `token_required` decorator work?
- **Answer**: It is a Python decorator using `functools.wraps`. It intercepts incoming requests before they reach the route handler, inspects `request.headers.get("Authorization")`, extracts the Bearer token, and decodes it using `jwt.decode`. If the token is valid, it retrieves the user from SQLite (`db.session.get(User, payload["sub"])`) and injects the user instance as the first argument into the wrapped route function. If invalid or expired, it immediately returns an HTTP 401 JSON error.
- **Follow-up Question**: *Why do we use `@wraps(f)` from `functools`?* (To preserve the original function's name and docstring, which Flask uses internally for endpoint routing).

#### Q15. How do you prevent SQL Injection in this application?
- **Answer**: We use **SQLAlchemy ORM**, which relies on parameterized queries. Instead of concatenating raw strings into SQL statements (e.g., `f"SELECT * FROM users WHERE email = '{email}'"`), SQLAlchemy separates the query structure from the user-supplied data: `User.query.filter_by(email=email)`. The database engine treats the parameters strictly as literal values, rendering SQL injection impossible.
- **Follow-up Question**: *Are there cases where SQLAlchemy could still be vulnerable to SQL injection?* (Yes, if a developer uses raw SQL queries via `db.session.execute(text(f"...{user_input}..."))` using f-strings instead of bind parameters).

#### Q16. How does your text preprocessor preserve technical terms like C++ and Node.js?
- **Answer**: Standard NLP tokenizers treat characters like `+`, `#`, and `.` as punctuation and strip them, turning `C++` into `C` and `.NET` into `NET`. In `text_preprocessor.py`, we maintain a `TECH_PROTECTED_TERMS` dictionary that substitutes these terms with temporary placeholders (e.g., `C++` $\rightarrow$ `cpp_token`, `Node.js` $\rightarrow$ `nodejs_token`) before punctuation removal, and restores them to their normalized technical format afterward.
- **Follow-up Question**: *How does this affect the TF-IDF vectorizer?* (By preserving `c++` and `node.js` as single distinct tokens, the vectorizer treats them as unique features in its vocabulary instead of confounding them with `c`).

#### Q17. What are the limitations of pure keyword matching in resume screening?
- **Answer**: Pure keyword matching suffers from two primary issues:
  1. **Vocabulary Mismatch**: It cannot detect synonyms (e.g., *"Postgres"* vs *"PostgreSQL"*, *"NLP"* vs *"Natural Language Processing"*, or *"predictive modeling"* vs *"machine learning"*).
  2. **Keyword Stuffing**: Candidates can game the system by pasting job requirements in tiny white fonts into the resume to artificially inflate word frequencies without demonstrating actual competence.
- **Follow-up Question**: *How does your platform counter keyword stuffing?* (By combining TF-IDF with semantic sentence embeddings and exact skill taxonomy verification—dense embeddings measure semantic context rather than word repetitions).

#### Q18. How did you structure your tests in pytest?
- **Answer**: We organized our tests into dedicated test modules under `tests/`: `test_auth.py`, `test_jobs.py`, `test_resume_parser.py`, `test_matching.py`, and `test_api.py`. We use pytest fixtures (`@pytest.fixture def client()`) in conjunction with an in-memory SQLite database (`sqlite:///:memory:`) so each test runs in complete isolation and leaves no residual data on disk.
- **Follow-up Question**: *What is the benefit of testing against an in-memory database?* (It executes in milliseconds because operations occur entirely in RAM without disk I/O, allowing all 30 tests to run in under 4 seconds).

#### Q19. How does `pypdf` extract text from PDF files?
- **Answer**: `pypdf` opens the PDF binary, parses the trailer and cross-reference table (`xref`), and accesses the root Document Catalog. It traverses the `/Pages` object tree to iterate over individual `/Page` dictionaries. For each page, it retrieves the `/Contents` stream, decompresses any zlib/Flate compression, interprets text-showing operators (like `Tj` and `TJ`), maps glyph identifiers to characters using the page's `/Font` `/ToUnicode` CMap, and concatenates the lines into a Unicode string.
- **Follow-up Question**: *Can `pypdf` extract text from a scanned document (image)?* (No, scanned PDFs contain bitmap images rather than encoded text streams. To extract text from scanned documents, an OCR engine like Tesseract is required).

#### Q20. How does `python-docx` extract text from DOCX files?
- **Answer**: A `.docx` file is an OpenXML file format compressed as a ZIP container. `python-docx` opens the archive, parses `word/document.xml` using `lxml`, and reads paragraph nodes (`<w:p>`) and run elements (`<w:r>`). It also iterates through table rows and cells (`<w:tbl>`, `<w:tr>`, `<w:tc>`) to extract structured text that candidates often put into column layouts.
- **Follow-up Question**: *Why is extracting text from tables important in resumes?* (Many modern resume templates use invisible two-column tables to align dates, companies, and skills; ignoring tables would omit large portions of the resume).

#### Q21. Explain the Application Factory pattern used in `backend/__init__.py`.
- **Answer**: Instead of creating the Flask `app` as a global variable at the module level, we wrap its creation inside a `create_app(config_class)` function. This pattern allows us to instantiate multiple independent app instances with different configurations—for example, passing `TestConfig` with an in-memory SQLite database during pytest, and `Config` with persistent disk storage during production.
- **Follow-up Question**: *How does the application factory prevent circular import issues?* (By deferring blueprint registration and model imports until inside the factory function when `db` is already initialized).

#### Q22. What are SQLAlchemy relationships and cascade deletes?
- **Answer**: SQLAlchemy relationships (`db.relationship`) define navigational links between related database models. For example, in our `Job` model:
  ```python
  matches = db.relationship("MatchResult", backref="job", cascade="all, delete-orphan")
  ```
  This creates an automatic `job.matches` collection. The `cascade="all, delete-orphan"` argument ensures that when a job is deleted, all associated `MatchResult` records are automatically removed by SQLAlchemy, preventing orphaned foreign key references.
- **Follow-up Question**: *What is an orphan record in database terminology?* (A child row whose foreign key points to a parent primary key that no longer exists).

#### Q23. How do you handle file size limits in Flask?
- **Answer**: We set `MAX_CONTENT_LENGTH = 10 * 1024 * 1024` (10 MB) in our `Config` class. When a client attempts to upload a file exceeding this limit, Flask immediately halts the incoming stream and triggers an HTTP `413 Request Entity Too Large` error, which our registered `@app.errorhandler(413)` intercepts to return a clean JSON error response.
- **Follow-up Question**: *Why is enforcing upload limits important for backend security?* (It prevents Denial of Service (DoS) attacks where attackers upload multi-gigabyte files to exhaust server memory and disk space).

#### Q24. How does the frontend communicate without React?
- **Answer**: We use modern **vanilla JavaScript (ES6+)** with the native `fetch()` API and DOM manipulation. We maintain state in JavaScript variables and update the UI by dynamically generating semantic HTML strings with `innerHTML` and template literals. To prevent XSS, all dynamic text content is escaped through an `escapeHtml()` helper before injection.
- **Follow-up Question**: *What is the advantage of using vanilla JavaScript for this project?* (Zero build step, no Node.js/npm bundling complexity, instant browser reloads, tiny footprint, and an architecture that any software engineer can immediately understand without framework-specific abstractions).

#### Q25. How do you ensure candidate scores remain bounded between 0% and 100%?
- **Answer**: Both TF-IDF and semantic embeddings calculate cosine similarity, which is theoretically bounded in $[0.0, 1.0]$ for non-negative text vectors. We apply `np.clip(score, 0.0, 1.0)` to eliminate any floating-point precision anomalies. The skill score is the ratio $\frac{\text{matched}}{\text{required}} \in [0.0, 1.0]$. The final composite score is calculated using normalized weights summing to 1.0 ($0.30 + 0.40 + 0.30 = 1.00$) and multiplied by 100, guaranteeing the final percentage strictly resides between $0\%$ and $100\%$.
- **Follow-up Question**: *What happens if a job has zero required skills specified?* (Our input validator rejects jobs without required skills; but as a safety measure, `skill_matcher.py` defaults to `1.0` if `total_required == 0` to prevent division-by-zero errors).

---

### 🔴 Advanced Questions (26 - 40)

#### Q26. Explain the architecture of `all-MiniLM-L6-v2` and how Sentence Transformers work.
- **Answer**: `all-MiniLM-L6-v2` is a 6-layer BERT-based transformer model distilled from a larger model. It uses self-attention mechanisms to generate contextual token representations. Unlike standard BERT, which requires cross-encoding sentence pairs through 12 layers simultaneously (computationally infeasible for thousands of candidate comparisons), Sentence Transformers use a **Siamese network architecture**. Each document is passed independently through the network to generate 384-dimensional dense vectors via mean pooling over token embeddings. Cosine similarity between two precomputed 384-d vectors can then be calculated in microseconds.
- **Follow-up Question**: *What is the time complexity of comparing $M$ resumes against $N$ jobs using Bi-Encoders vs Cross-Encoders?* (Bi-Encoders take $O(M + N)$ embeddings calculations plus $O(M \times N)$ vector dot products. Cross-Encoders require $O(M \times N)$ full transformer forward passes, which is thousands of times slower).

#### Q27. What happens when a resume is 10 pages long and exceeds the 512-token limit of Sentence Transformers?
- **Answer**: Standard BERT models have an input position embedding limit of 512 tokens. If you pass an entire multi-page resume into the model at once, everything beyond the 512th token is silently truncated. In `semantic_matcher.py`, we implemented a **chunking strategy**: long documents are split into logical paragraphs or 100-word chunks, each chunk is encoded into an embedding vector independently, and the mean vector of all chunks represents the document. This ensures that skills and experiences listed on page 2 or 3 are fully captured.
- **Follow-up Question**: *What is mean pooling vs CLS pooling in transformer representations?* (CLS pooling uses the first `[CLS]` token's hidden state as the sentence representation. Mean pooling averages all contextualized token vectors across the attention mask, which empirical research shows produces significantly higher semantic search performance).

#### Q28. How does your system explain the AI matching score to recruiters?
- **Answer**: Rather than returning a black-box percentage, the `CandidateScorer` produces an explainable report:
  1. **Component Breakdown**: It outputs the individual scores for TF-IDF, Semantic AI, and Skill Match.
  2. **Point Contribution**: Shows the exact weighted contribution (e.g., TF-IDF contributes $+16.8$ points, Semantic contributes $+20.3$ points, Skill contributes $+30.0$ points towards an overall score of $67.1\%$).
  3. **Skill Audit**: Explicitly lists matched skills in green badges and missing requirements in red badges.
  4. **Domain Clustering**: Categorizes skills into domain clusters (e.g., Backend, Frontend, Cloud/DevOps, AI/ML) and reports strong alignments and weak areas.
- **Follow-up Question**: *Why is explainability critical in recruitment AI systems?* (To comply with employment regulations like the EU AI Act and NYC Local Law 144, ensure hiring transparency, eliminate algorithmic bias, and allow recruiters to justify decisions to hiring managers).

#### Q29. How would you scale this application to handle 50,000 resume uploads per day?
- **Answer**: 
  1. **Asynchronous Architecture**: Replace synchronous uploads with background task workers using **Celery and Redis/RabbitMQ**. When a resume is uploaded, the API saves the file to object storage (like AWS S3 or Google Cloud Storage) and enqueues a `parse_and_score_task`.
  2. **Vector Database**: Instead of computing sentence embeddings on the fly, store candidate 384-d vectors in a specialized vector database like **Qdrant, Pinecone, or Milvus**. Vector indexes (such as HNSW - Hierarchical Navigable Small World) can search and rank top-100 candidates among millions in under 10 milliseconds.
  3. **Relational Database Scaling**: Migrate SQLite to a managed **PostgreSQL** instance with read replicas and connection pooling (PgBouncer).
  4. **Containerization**: Deploy stateless Flask worker containers across Kubernetes pods managed by an autoscaler.
- **Follow-up Question**: *What is HNSW and why is it faster than exhaustive flat search?* (Hierarchical Navigable Small World is a multi-layer graph data structure that performs approximate nearest neighbor search in $O(\log N)$ time instead of $O(N)$ brute-force linear search).

#### Q30. How would you detect and mitigate algorithmic bias in this resume screening tool?
- **Answer**:
  1. **Name and Demographic Blind Screening**: Strip candidate names, gender pronouns, physical addresses, age/birth years, and university names before running NLP matching.
  2. **Audit Metric Disparities**: Implement an **Adverse Impact Analysis** (the 4/5ths or 80% rule) to verify that selection rates for protected demographic groups do not fall below 80% of the highest group's selection rate.
  3. **Embedding Debiasing**: Standard pretrained sentence transformers can exhibit gender bias (e.g., associating masculine pronouns with engineering roles). Using domain-specific fine-tuning with debiased projection matrices removes gender-correlated vectors from technical skill dimensions.
- **Follow-up Question**: *What is NYC Local Law 144?* (A regulation requiring automated employment decision tools (AEDTs) to undergo an annual independent bias audit before being used to screen candidates for employment in New York City).

#### Q31. What is the difference between Lemmatization and Stemming, and why didn't you use aggressive stemming?
- **Answer**: **Stemming** uses heuristic rule-based trimming to chop off word suffixes (e.g., Porter Stemmer converts *"running"*, *"runs"*, *"runner"* to *"run"*), often creating non-words (e.g., *"university"* $\rightarrow$ *"univers"*). **Lemmatization** uses a morphological dictionary to reduce words to their true base lemma (e.g., *"better"* $\rightarrow$ *"good"*). In technical domains, aggressive stemming corrupts technical acronyms and terms—such as conflating *"Data"* with *"Database"* or breaking framework names. Our customized preprocessor preserves exact technical tokens while using TF-IDF n-grams to handle inflectional variations cleanly.
- **Follow-up Question**: *What is WordNet and how is it used in lemmatization?* (WordNet is a lexical database of English words grouped into sets of cognitive synonyms called synsets, providing grammatical category and semantic relation mappings for lemmatizers like NLTK's WordNetLemmatizer).

#### Q32. How would you handle multilingual resumes (e.g., French, German, Spanish)?
- **Answer**: 
  1. Detect the resume language using `langdetect` or `fasttext`.
  2. Switch the Sentence Transformer model from `all-MiniLM-L6-v2` (monolingual English) to a multilingual model such as `paraphrase-multilingual-MiniLM-L12-v2`. This model maps 50+ languages into a shared vector space, allowing an English job posting to match a candidate's Spanish or French resume directly based on semantic meaning.
  3. Extend stop-word lists and skill synonym dictionaries with multilingual mappings.
- **Follow-up Question**: *Does cross-lingual sentence embedding performance degrade compared to monolingual models?* (There is a minor performance trade-off of ~2-5% on pure English tasks due to the multilingual model's parameter capacity being distributed across multiple languages).

#### Q33. What is the difference between WSGI and ASGI, and how would you deploy Flask in production?
- **Answer**: Flask is built on **WSGI (Web Server Gateway Interface)**, a synchronous standard where each worker thread processes one request at a time. **ASGI (Asynchronous Server Gateway Interface)** supports asynchronous event loops (`asyncio`) and WebSockets. For production deployment, we would run Flask behind a production WSGI server like **Gunicorn** or **uWSGI** with multiple worker processes (e.g., `2 * CPU_CORES + 1`), positioned behind an **NGINX** reverse proxy for SSL termination, static file caching, and DDoS rate limiting.
- **Follow-up Question**: *Why shouldn't Flask's built-in development server (`app.run()`) ever be used in production?* (The development server is single-threaded or basic multi-threaded, not hardened against slowloris attacks, leaks memory under prolonged load, and does not handle process recycling or worker crashes).

#### Q34. How did you structure database indexing and why?
- **Answer**: In `backend/models.py`, we placed an explicit unique index on `User.email` (`index=True`) and foreign keys with indices on `MatchResult.job_id` and `MatchResult.resume_id`. Without an index on `job_id`, retrieving candidates for a job (`GET /api/jobs/<job_id>/candidates`) requires a Full Table Scan ($O(N)$ time). With a B-Tree index on `job_id`, the database locates candidate rows in $O(\log N)$ time, ensuring constant sub-millisecond query performance even with tens of thousands of match records.
- **Follow-up Question**: *What is the trade-off of adding too many indices to a database table?* (While indices accelerate `SELECT` read queries, they slow down `INSERT`, `UPDATE`, and `DELETE` operations because the B-Tree index structure must be recalculated and written to disk on every modification).

#### Q35. How does your application protect against Cross-Site Scripting (XSS)?
- **Answer**: XSS occurs when untrusted user input is rendered into the browser DOM without sanitization, allowing attackers to execute arbitrary JavaScript (such as stealing JWT tokens from `localStorage`). In our frontend JavaScript (`candidates.js`, `dashboard.js`, `jobs.js`), we created and used an `escapeHtml()` utility that replaces HTML control characters (`&`, `<`, `>`, `"`, `'`) with their respective character entity references (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#039;`) before injecting candidate names or descriptions into the DOM.
- **Follow-up Question**: *Where is the safest place to store authentication tokens to completely prevent XSS-based theft?* (In an `HttpOnly`, `Secure`, `SameSite=Strict` cookie, which cannot be read or manipulated by client-side JavaScript).

#### Q36. What is the difference between overfitting and underfitting in NLP models?
- **Answer**: In machine learning, **overfitting** occurs when a model memorizes the training data's noise and specifics, failing to generalize to new data (high variance). **Underfitting** occurs when the model is too simple to capture the underlying patterns (high bias). In our platform, because we use a frozen, pre-trained Sentence Transformer model (`all-MiniLM-L6-v2`) fine-tuned on over a billion sentence pairs, it possesses high generalization without risk of overfitting on a small dataset of local job descriptions.
- **Follow-up Question**: *What is fine-tuning vs zero-shot inference?* (Zero-shot inference uses a pre-trained model directly without any task-specific weight updates. Fine-tuning continues gradient descent training on a specific labeled dataset to adjust model weights for that domain).

#### Q37. If two candidates have the same skills, what determines their rank?
- **Answer**: While their **Skill Match Score** will be identical, their overall scores will differ based on **TF-IDF Keyword Similarity** and **Semantic AI Similarity**. A candidate whose resume describes in-depth accomplishments, methodologies, and context matching the job description will score higher on TF-IDF density and sentence embeddings than a candidate who merely lists skills in a bulleted footer.
- **Follow-up Question**: *How could you incorporate candidate years of experience into the scoring formula?* (By extracting numerical date ranges or years of experience using regex, comparing it against the job's minimum experience, and adding an experience multiplier or penalty component).

#### Q38. How would you implement real-time matching progress updates for 1,000 resumes?
- **Answer**: Instead of a blocking HTTP request that might time out after 30 seconds, we would use **Server-Sent Events (SSE)** or **WebSockets**. When the recruiter clicks *"Match All"*, the backend assigns a `job_execution_id` and publishes progress events over an SSE channel (`/api/match-progress/<job_id>`). The frontend listens via `EventSource` and increments a live progress bar: *"Scored 245 / 1000 resumes (24%)"*.
- **Follow-up Question**: *Why choose Server-Sent Events over WebSockets for progress updates?* (SSE is simpler, runs over standard HTTP, includes automatic reconnection, and is unidirectional from server to client, which matches the progress notification pattern perfectly).

#### Q39. How do you handle database migrations when adding new columns to models?
- **Answer**: In development with SQLite, `db.create_all()` creates tables that do not exist, but does not alter existing tables. In production, we use **Flask-Migrate** (built on **Alembic**). When a model changes (e.g., adding `candidate_linkedin` to `Resume`), Alembic detects the schema diff, generates an auto-versioned migration script with `upgrade()` and `downgrade()` functions, and applies the schema changes to the live database without data loss.
- **Follow-up Question**: *What is the difference between schema migrations in relational databases vs NoSQL document stores?* (Relational databases enforce strict schemas where changes require explicit `ALTER TABLE` DDL operations. NoSQL document stores like MongoDB are schema-less, meaning documents in the same collection can have different fields, shifting schema migration responsibility to application code).

#### Q40. Summarize the biggest engineering lesson you learned building this platform.
- **Answer**: *"The biggest engineering takeaway was that a successful AI system is not defined by raw neural network complexity alone, but by **layered, resilient design and explainability**. At first, it might be tempting to just throw an LLM or deep transformer at the resume. However, pure deep learning can be slow, hallucinate, and fail to explain why a candidate was ranked #1. By combining three orthogonal layers—deterministic skill verification, classical TF-IDF statistical frequency, and contextual dense embeddings—the platform achieves both high semantic accuracy and 100% transparent explainability that recruiters can trust and debug. Additionally, building resilient fallback systems ensures that network hiccups or cold-start model downloads never bring down the core application."*
- **Follow-up Question**: *What feature would you build next if you had two more weeks?* (I would integrate an asynchronous Celery task queue with a vector database like Qdrant to scale the search to 100,000+ candidates with millisecond sub-linear query times).

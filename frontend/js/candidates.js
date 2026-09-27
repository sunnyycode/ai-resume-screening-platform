// Candidates & Resume Screening Logic

let currentJobId = null;
let allJobs = [];

// Initialize URL params (e.g. ?job_id=1)
function getUrlParam(param) {
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

async function loadJobSelector() {
    const selector = document.getElementById("jobSelect");
    const uploadJobSelect = document.getElementById("uploadJobSelect");
    if (!selector) return;

    try {
        const res = await authFetch("/api/jobs");
        const data = await res.json();

        if (data.success && data.jobs.length > 0) {
            allJobs = data.jobs;
            selector.innerHTML = data.jobs.map(j => 
                `<option value="${j.id}">${escapeHtml(j.title)} (ID: ${j.id})</option>`
            ).join("");

            if (uploadJobSelect) {
                uploadJobSelect.innerHTML = `<option value="">-- None (Upload Only) --</option>` +
                    data.jobs.map(j => `<option value="${j.id}">${escapeHtml(j.title)}</option>`).join("");
            }

            // Check if job_id was in query string
            const qJobId = getUrlParam("job_id");
            if (qJobId && allJobs.some(j => j.id == qJobId)) {
                selector.value = qJobId;
                currentJobId = parseInt(qJobId);
            } else {
                currentJobId = data.jobs[0].id;
            }

            updateSelectedJobDetails();
            loadCandidates();
        } else {
            selector.innerHTML = `<option value="">No jobs available. Create one first.</option>`;
            document.getElementById("candidatesTableBody").innerHTML = `
                <tr><td colspan="7" style="text-align: center; padding: 2rem;">Please create a job posting first.</td></tr>
            `;
        }
    } catch (err) {
        console.error("Failed to load jobs selector:", err);
    }
}

function updateSelectedJobDetails() {
    const job = allJobs.find(j => j.id === currentJobId);
    const container = document.getElementById("currentJobInfo");
    if (!container || !job) return;

    const skills = (job.required_skills || []).map(s => 
        `<span class="skill-tag">${escapeHtml(s)}</span>`
    ).join("");

    container.innerHTML = `
        <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.2rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
                <h3 style="font-size: 1.2rem;">${escapeHtml(job.title)}</h3>
                <button onclick="matchAllCandidates()" class="btn btn-secondary btn-sm" id="btnMatchAll">
                    ⚡ Re-evaluate All Resumes
                </button>
            </div>
            <div style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 0.6rem;">
                ${escapeHtml(job.description.substring(0, 180))}...
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;">
                <strong style="font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase;">Required Skills:</strong>
                ${skills}
            </div>
        </div>
    `;
}

async function loadCandidates() {
    if (!currentJobId) return;

    const tbody = document.getElementById("candidatesTableBody");
    const minScore = document.getElementById("filterMinScore").value;
    const skillFilter = document.getElementById("filterSkill").value.trim();
    const search = document.getElementById("filterSearch").value.trim();
    const sort = document.getElementById("filterSort").value;

    let url = `/api/jobs/${currentJobId}/candidates?sort=${sort}`;
    if (minScore) url += `&min_score=${encodeURIComponent(minScore)}`;
    if (skillFilter) url += `&skill=${encodeURIComponent(skillFilter)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem;">Loading candidates...</td></tr>`;

    try {
        const res = await authFetch(url);
        const data = await res.json();

        if (!data.success) {
            tbody.innerHTML = `<tr><td colspan="7" style="color: var(--danger); text-align: center; padding: 1.5rem;">${escapeHtml(data.error)}</td></tr>`;
            return;
        }

        document.getElementById("candidateCount").innerText = `${data.total_candidates} Candidates Ranked`;

        if (data.candidates.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                        No matching candidates found for this criteria.<br/>
                        <button onclick="openUploadModal()" class="btn btn-primary btn-sm" style="margin-top: 1rem;">
                            Upload Resumes to Match
                        </button>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.candidates.map(c => {
            let scoreColor = "var(--success)";
            let badgeClass = "badge-success";
            if (c.overall_score < 60) {
                scoreColor = "var(--danger)";
                badgeClass = "badge-danger";
            } else if (c.overall_score < 80) {
                scoreColor = "var(--warning)";
                badgeClass = "badge-warning";
            }

            const matchedPills = (c.matched_skills || []).map(s => 
                `<span class="skill-tag matched">${escapeHtml(s)}</span>`
            ).join("");

            const missingPills = (c.missing_skills || []).map(s => 
                `<span class="skill-tag missing">${escapeHtml(s)}</span>`
            ).join("");

            return `
                <tr>
                    <td><strong style="color: var(--primary);">#${c.rank}</strong></td>
                    <td>
                        <strong>${escapeHtml(c.candidate_name)}</strong>
                        ${c.candidate_email ? `<div style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(c.candidate_email)}</div>` : ''}
                    </td>
                    <td>
                        <div class="score-meter">
                            <div class="score-bar-bg" style="width: 70px;">
                                <div class="score-bar-fill" style="width: ${c.overall_score}%; background: ${scoreColor};"></div>
                            </div>
                            <span class="badge ${badgeClass}">${c.overall_score}%</span>
                        </div>
                    </td>
                    <td>
                        <div style="font-size: 0.85rem; line-height: 1.4;">
                            <div>TF-IDF: <strong>${Math.round(c.tfidf_score * 100)}%</strong></div>
                            <div>Semantic: <strong>${Math.round(c.semantic_score * 100)}%</strong></div>
                            <div>Skill: <strong>${Math.round(c.skill_score * 100)}%</strong></div>
                        </div>
                    </td>
                    <td style="max-width: 220px;">
                        <div style="max-height: 70px; overflow-y: auto;">
                            ${matchedPills || '<span style="color: var(--text-muted); font-size: 0.8rem;">None</span>'}
                        </div>
                    </td>
                    <td style="max-width: 200px;">
                        <div style="max-height: 70px; overflow-y: auto;">
                            ${missingPills || '<span style="color: var(--success); font-size: 0.8rem;">None missing!</span>'}
                        </div>
                    </td>
                    <td>
                        <a href="/candidate-details?match_id=${c.id}" class="btn btn-primary btn-sm">
                            Analyze
                        </a>
                    </td>
                </tr>
            `;
        }).join("");

    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" style="color: var(--danger); text-align: center;">Network error: ${err.message}</td></tr>`;
    }
}

async function matchAllCandidates() {
    if (!currentJobId) return;

    const btn = document.getElementById("btnMatchAll");
    if (btn) {
        btn.disabled = true;
        btn.innerText = "Evaluating...";
    }

    try {
        const res = await authFetch(`/api/jobs/${currentJobId}/match-all`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            loadCandidates();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (err) {
        alert(`Evaluation failed: ${err.message}`);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "⚡ Re-evaluate All Resumes";
        }
    }
}

function exportCandidatesCSV() {
    if (!currentJobId) {
        alert("Please select a job first to export candidate results.");
        return;
    }
    window.location.href = `/api/jobs/${currentJobId}/export`;
}

// Modal controls
function openUploadModal() {
    const modal = document.getElementById("uploadModal");
    if (modal) {
        modal.classList.add("active");
        if (currentJobId && document.getElementById("uploadJobSelect")) {
            document.getElementById("uploadJobSelect").value = currentJobId;
        }
    }
}

function closeUploadModal() {
    const modal = document.getElementById("uploadModal");
    if (modal) modal.classList.remove("active");
    const alertBox = document.getElementById("uploadAlert");
    if (alertBox) alertBox.innerHTML = "";
    const form = document.getElementById("resumeUploadForm");
    if (form) form.reset();
}

// Handle Resume File Upload
async function handleResumeUpload(event) {
    event.preventDefault();

    const fileInput = document.getElementById("resumeFile");
    const nameInput = document.getElementById("candidateName");
    const jobSelect = document.getElementById("uploadJobSelect");
    const alertBox = document.getElementById("uploadAlert");
    const submitBtn = document.getElementById("uploadSubmitBtn");

    if (!fileInput.files || fileInput.files.length === 0) {
        alertBox.innerHTML = `<div class="alert alert-danger">Please choose a resume file to upload.</div>`;
        return;
    }

    const file = fileInput.files[0];
    const allowed = ["pdf", "docx", "txt"];
    const ext = file.name.split(".").pop().toLowerCase();
    if (!allowed.includes(ext)) {
        alertBox.innerHTML = `<div class="alert alert-danger">Invalid file type .${ext}. Only PDF, DOCX, and TXT are supported.</div>`;
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    if (nameInput.value.trim()) {
        formData.append("candidate_name", nameInput.value.trim());
    }
    if (jobSelect.value) {
        formData.append("job_id", jobSelect.value);
    }

    submitBtn.disabled = true;
    submitBtn.innerText = "Parsing & Matching...";
    alertBox.innerHTML = `<div class="alert alert-info">Extracting resume text and running NLP pipeline...</div>`;

    try {
        const token = getToken();
        const headers = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const res = await fetch("/api/resumes/upload", {
            method: "POST",
            headers: headers,
            body: formData
        });

        const data = await res.json();

        if (data.success) {
            alertBox.innerHTML = `<div class="alert alert-success">Resume uploaded & processed successfully!</div>`;
            setTimeout(() => {
                closeUploadModal();
                loadCandidates();
            }, 1200);
        } else {
            alertBox.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error)}</div>`;
        }
    } catch (err) {
        alertBox.innerHTML = `<div class="alert alert-danger">Upload failed: ${err.message}</div>`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Upload & Match";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadJobSelector();

    const jobSelect = document.getElementById("jobSelect");
    if (jobSelect) {
        jobSelect.addEventListener("change", (e) => {
            currentJobId = parseInt(e.target.value);
            updateSelectedJobDetails();
            loadCandidates();
        });
    }

    // Filter listeners
    ["filterMinScore", "filterSkill", "filterSearch", "filterSort"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                loadCandidates();
            });
        }
    });

    const uploadForm = document.getElementById("resumeUploadForm");
    if (uploadForm) {
        uploadForm.addEventListener("submit", handleResumeUpload);
    }
});

// Job Management Logic

async function loadJobsList() {
    const container = document.getElementById("jobsList");
    if (!container) return;

    container.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading jobs...</div>`;

    try {
        const res = await authFetch("/api/jobs");
        const data = await res.json();

        if (!data.success) {
            container.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error)}</div>`;
            return;
        }

        if (data.jobs.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; background: var(--surface); border: 1px dashed var(--border); border-radius: var(--radius);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
                    <h3 style="margin-bottom: 0.5rem;">No jobs posted yet</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Create your first job posting to start matching candidate resumes.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.jobs.map(job => {
            const reqSkills = (job.required_skills || []).map(s => 
                `<span class="skill-tag">${escapeHtml(s)}</span>`
            ).join("");

            const prefSkills = (job.preferred_skills || []).map(s => 
                `<span class="skill-tag" style="background: #f1f5f9; color: #475569;">${escapeHtml(s)}</span>`
            ).join("");

            return `
                <div class="card" style="margin-bottom: 1.2rem;">
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.8rem;">
                            <div>
                                <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.3rem;">
                                    ${escapeHtml(job.title)}
                                </h3>
                                <div style="display: flex; gap: 1rem; font-size: 0.85rem; color: var(--text-secondary);">
                                    <span>💼 Experience: <strong>${escapeHtml(job.experience)}</strong></span>
                                    <span>🎓 Education: <strong>${escapeHtml(job.education)}</strong></span>
                                    <span>👥 Candidates Evaluated: <strong>${job.candidate_count || 0}</strong></span>
                                </div>
                            </div>
                            <div style="display: flex; gap: 0.5rem;">
                                <a href="/candidates?job_id=${job.id}" class="btn btn-primary btn-sm">
                                    View Candidates
                                </a>
                                <button onclick="deleteJob(${job.id})" class="btn btn-danger btn-sm" title="Delete Job">
                                    🗑️
                                </button>
                            </div>
                        </div>

                        <p style="font-size: 0.93rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1rem; max-height: 80px; overflow: hidden; text-overflow: ellipsis;">
                            ${escapeHtml(job.description)}
                        </p>

                        <div>
                            <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.3rem;">
                                Required Skills
                            </div>
                            <div style="margin-bottom: 0.5rem;">${reqSkills || '<span style="color: var(--text-muted); font-size: 0.85rem;">None specified</span>'}</div>
                            
                            ${prefSkills ? `
                                <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.3rem;">
                                    Preferred Skills
                                </div>
                                <div>${prefSkills}</div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join("");

    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Network error loading jobs: ${err.message}</div>`;
    }
}

async function handleCreateJob(event) {
    event.preventDefault();

    const title = document.getElementById("jobTitle").value.trim();
    const description = document.getElementById("jobDesc").value.trim();
    const skillsInput = document.getElementById("jobSkills").value.trim();
    const prefSkillsInput = document.getElementById("prefSkills").value.trim();
    const experience = document.getElementById("jobExp").value.trim();
    const education = document.getElementById("jobEdu").value.trim();
    const alertBox = document.getElementById("jobAlert");

    alertBox.innerHTML = "";

    if (!title) {
        alertBox.innerHTML = `<div class="alert alert-danger">Please enter a job title.</div>`;
        return;
    }
    if (!description || description.length < 20) {
        alertBox.innerHTML = `<div class="alert alert-danger">Job description must be at least 20 characters.</div>`;
        return;
    }
    if (!skillsInput) {
        alertBox.innerHTML = `<div class="alert alert-danger">Please specify at least one required skill.</div>`;
        return;
    }

    const requiredSkills = skillsInput.split(",").map(s => s.trim()).filter(Boolean);
    const preferredSkills = prefSkillsInput ? prefSkillsInput.split(",").map(s => s.trim()).filter(Boolean) : [];

    const payload = {
        title: title,
        description: description,
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        experience: experience || "0-2 years",
        education: education || "Bachelor's Degree"
    };

    try {
        const res = await authFetch("/api/jobs", {
            method: "POST",
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            alertBox.innerHTML = `<div class="alert alert-success">Job created successfully!</div>`;
            document.getElementById("createJobForm").reset();
            loadJobsList();
            setTimeout(() => { alertBox.innerHTML = ""; }, 3000);
        } else {
            alertBox.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error)}</div>`;
        }
    } catch (err) {
        alertBox.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
    }
}

async function deleteJob(jobId) {
    if (!confirm("Are you sure you want to delete this job posting and its candidate match records?")) {
        return;
    }

    try {
        const res = await authFetch(`/api/jobs/${jobId}`, {
            method: "DELETE"
        });
        const data = await res.json();

        if (data.success) {
            loadJobsList();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (err) {
        alert(`Network error: ${err.message}`);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadJobsList();
    const jobForm = document.getElementById("createJobForm");
    if (jobForm) {
        jobForm.addEventListener("submit", handleCreateJob);
    }
});

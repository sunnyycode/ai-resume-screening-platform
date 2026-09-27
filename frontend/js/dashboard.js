// Recruiter Dashboard Logic

async function loadDashboard() {
    try {
        const res = await authFetch("/api/dashboard/stats");
        const data = await res.json();

        if (!data.success) {
            console.error("Dashboard error:", data.error);
            return;
        }

        const stats = data.stats;
        document.getElementById("statTotalJobs").innerText = stats.total_jobs;
        document.getElementById("statTotalCandidates").innerText = stats.total_candidates;
        document.getElementById("statAvgScore").innerText = `${stats.average_match_score}%`;
        document.getElementById("statEvaluations").innerText = stats.total_evaluations;

        renderSkillAnalytics(stats.top_demanded_skills || [], stats.top_candidate_skills || []);
        renderTopCandidates(data.top_candidates || []);
    } catch (err) {
        console.error("Failed to load dashboard metrics:", err);
    }
}

function renderSkillAnalytics(demanded, candidatePool) {
    const demandContainer = document.getElementById("demandSkillsList");
    const candidateContainer = document.getElementById("candidateSkillsList");

    if (demandContainer) {
        if (demanded.length === 0) {
            demandContainer.innerHTML = `<span style="color: var(--text-muted); font-size: 0.85rem;">No job skills registered yet.</span>`;
        } else {
            const maxDemand = Math.max(...demanded.map(d => d.count), 1);
            demandContainer.innerHTML = demanded.map(d => `
                <div style="margin-bottom: 0.7rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.2rem;">
                        <strong>${escapeHtml(d.skill)}</strong>
                        <span style="color: var(--text-secondary); font-size: 0.8rem;">${d.count} job(s)</span>
                    </div>
                    <div class="score-bar-bg" style="height: 6px;">
                        <div class="score-bar-fill" style="width: ${(d.count / maxDemand) * 100}%; background: var(--primary);"></div>
                    </div>
                </div>
            `).join("");
        }
    }

    if (candidateContainer) {
        if (candidatePool.length === 0) {
            candidateContainer.innerHTML = `<span style="color: var(--text-muted); font-size: 0.85rem;">No resumes analyzed yet.</span>`;
        } else {
            const maxCand = Math.max(...candidatePool.map(c => c.count), 1);
            candidateContainer.innerHTML = candidatePool.map(c => `
                <div style="margin-bottom: 0.7rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 0.2rem;">
                        <strong>${escapeHtml(c.skill)}</strong>
                        <span style="color: var(--text-secondary); font-size: 0.8rem;">${c.count} candidate(s)</span>
                    </div>
                    <div class="score-bar-bg" style="height: 6px;">
                        <div class="score-bar-fill" style="width: ${(c.count / maxCand) * 100}%; background: var(--success);"></div>
                    </div>
                </div>
            `).join("");
        }
    }
}

function renderTopCandidates(candidates) {
    const tableBody = document.getElementById("topCandidatesBody");
    if (!tableBody) return;

    if (candidates.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                    No candidates evaluated yet. Upload a resume or run matching on a job.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = candidates.map(c => {
        let badgeClass = "badge-success";
        if (c.overall_score < 60) badgeClass = "badge-danger";
        else if (c.overall_score < 80) badgeClass = "badge-warning";

        const matchedTags = (c.matched_skills || []).slice(0, 3).map(s => 
            `<span class="skill-tag matched">${escapeHtml(s)}</span>`
        ).join("") + ((c.matched_skills || []).length > 3 ? `<span class="skill-tag">+${c.matched_skills.length - 3}</span>` : "");

        const missingTags = (c.missing_skills || []).slice(0, 3).map(s => 
            `<span class="skill-tag missing">${escapeHtml(s)}</span>`
        ).join("") + ((c.missing_skills || []).length > 3 ? `<span class="skill-tag missing">+${c.missing_skills.length - 3}</span>` : "");

        return `
            <tr>
                <td><strong>${escapeHtml(c.candidate_name)}</strong></td>
                <td><span style="font-size: 0.85rem; color: var(--text-secondary);">${escapeHtml(c.job_title)}</span></td>
                <td>
                    <div class="score-meter">
                        <div class="score-bar-bg" style="width: 80px;">
                            <div class="score-bar-fill" style="width: ${c.overall_score}%; background: ${c.overall_score >= 80 ? 'var(--success)' : c.overall_score >= 60 ? 'var(--warning)' : 'var(--danger)'};"></div>
                        </div>
                        <span class="badge ${badgeClass}">${c.overall_score}%</span>
                    </div>
                </td>
                <td>${matchedTags || '<span style="color: var(--text-muted); font-size: 0.8rem;">None</span>'}</td>
                <td>${missingTags || '<span style="color: var(--text-muted); font-size: 0.8rem;">None</span>'}</td>
                <td>
                    <a href="/candidate-details?match_id=${c.id}" class="btn btn-secondary btn-sm">
                        View Analysis
                    </a>
                </td>
            </tr>
        `;
    }).join("");
}

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

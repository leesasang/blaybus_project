(function () {
  const API_BASE = "http://127.0.0.1:8000";

  async function apiFetch(path, opts, allowRetry) {
    opts = opts || {};
    if (allowRetry === undefined) allowRetry = true;
    const headers = Object.assign({}, opts.headers || {});
    if (opts.body && typeof opts.body === "object" && !(opts.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
      opts = Object.assign({}, opts, { body: JSON.stringify(opts.body) });
    }
    const token = localStorage.getItem("bug_token");
    if (token) headers["Authorization"] = "Bearer " + token;
    const res = await fetch(API_BASE + path, Object.assign({}, opts, { headers }));
    if (res.status === 401 && allowRetry && path !== "/auth/me") {
      localStorage.removeItem("bug_token");
      await ensureAuth();
      return apiFetch(path, opts, false);
    }
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || res.statusText);
    }
    const ct = res.headers.get("content-type");
    if (ct && ct.indexOf("application/json") !== -1) return res.json();
    return res.text();
  }

  async function register(email, password, nickname) {
    return apiFetch("/users/", { method: "POST", body: { email, nickname, password } });
  }

  async function login(email, password) {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);
    const res = await fetch(API_BASE + "/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    localStorage.setItem("bug_token", data.access_token);
    return data;
  }

  async function ensureAuth() {
    const t = localStorage.getItem("bug_token");
    if (t) {
      try {
        const check = await fetch(API_BASE + "/auth/me", {
          headers: { Authorization: "Bearer " + t },
        });
        if (check.ok) return;
        if (check.status === 401 || check.status === 403) {
          localStorage.removeItem("bug_token");
        } else {
          return;
        }
      } catch (e) {
        localStorage.removeItem("bug_token");
      }
    }
    const email = "demo@bug.site";
    const password = "demo123456";
    const nickname = "데모유저";
    try {
      await login(email, password);
    } catch (e) {
      await register(email, password, nickname);
      await login(email, password);
    }
  }

  function clearProject() {
    sessionStorage.removeItem("bug_project_id");
  }

  async function createProject(prompt) {
    return apiFetch("/projects/", { method: "POST", body: { prompt } });
  }

  async function createPlotJob(projectId, prompt) {
    return apiFetch("/api/v1/jobs/plot-generation", {
      method: "POST",
      body: { project_id: projectId, prompt },
    });
  }

  async function createTextToImageJob(projectId, prompt, extra) {
    const body = Object.assign(
      {
        project_id: projectId,
        prompt,
        negative_prompt: "",
        width: 512,
        height: 512,
      },
      extra || {}
    );
    return apiFetch("/api/v1/jobs/text-to-image", { method: "POST", body });
  }

  async function createTextToImageToVideoJob(projectId, prompt, extra) {
    const body = Object.assign(
      {
        project_id: projectId,
        prompt,
        negative_prompt: "",
      },
      extra || {}
    );
    return apiFetch("/api/v1/jobs/text-to-image-to-video", { method: "POST", body });
  }

  async function getJob(jobId) {
    return apiFetch("/api/v1/jobs/" + jobId, { method: "GET" });
  }

  async function fetchJobOutputs(jobId) {
    return apiFetch("/api/v1/jobs/" + jobId + "/outputs", { method: "GET" });
  }

  async function pollJob(jobId, options) {
    const interval = (options && options.interval) || 1500;
    const maxAttempts = (options && options.maxAttempts) || 200;
    for (let i = 0; i < maxAttempts; i++) {
      const job = await getJob(jobId);
      if (job.status === "completed" || job.status === "failed") return job;
      await new Promise(function (r) {
        setTimeout(r, interval);
      });
    }
    throw new Error("작업 시간 초과");
  }

  window.BugSiteApi = {
    API_BASE,
    ensureAuth,
    clearProject,
    createProject,
    createPlotJob,
    createTextToImageJob,
    createTextToImageToVideoJob,
    getJob,
    fetchJobOutputs,
    pollJob,
  };
})();

(function () {
  const chat = document.getElementById("chat");
  const msg = document.getElementById("msg");
  const send = document.getElementById("send");
  const exportBtn = document.getElementById("exportBtn");

  if (!chat || !msg || !send) return;

  const chips = Array.from(document.querySelectorAll(".chip[data-step]"));
  let currentStep = "storyboard";

  function setStep(step) {
    currentStep = step;
    chips.forEach(function (c) {
      c.classList.toggle("active", c.dataset.step === step);
    });
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function (m) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[m];
    });
  }

  function timeLabel() {
    const d = new Date();
    return d.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });
  }

  function appendMe(text) {
    const row = document.createElement("div");
    row.className = "msgRow me";
    row.innerHTML =
      '<div class="bubble"><p>' +
      escapeHtml(text) +
      '</p><div class="meta">나 · ' +
      timeLabel() +
      "</div></div>";
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  function appendAI(text) {
    const row = document.createElement("div");
    row.className = "msgRow ai";
    row.innerHTML =
      '<div class="bubble"><p>' +
      escapeHtml(text) +
      '</p><div class="meta">AI · ' +
      timeLabel() +
      "</div></div>";
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  function appendAIHtml(html) {
    const row = document.createElement("div");
    row.className = "msgRow ai";
    row.innerHTML =
      '<div class="bubble"><div class="body">' +
      html +
      '</div><div class="meta">AI · ' +
      timeLabel() +
      "</div></div>";
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  function autosize(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 140) + "px";
  }

  msg.addEventListener("input", function () {
    autosize(msg);
  });

  function getOrCreateProjectId(userPrompt) {
    let pid = sessionStorage.getItem("bug_project_id");
    if (pid) return Promise.resolve(pid);
    return window.BugSiteApi.createProject(userPrompt).then(function (p) {
      sessionStorage.setItem("bug_project_id", p.id);
      return p.id;
    });
  }

  function handleStoryboardApi(text) {
    return window.BugSiteApi.ensureAuth().then(function () {
      return getOrCreateProjectId(text);
    }).then(function (projectId) {
      return window.BugSiteApi.createPlotJob(projectId, text);
    }).then(function (job) {
      return window.BugSiteApi.pollJob(job.id);
    }).then(function (job) {
      if (job.status === "failed") {
        throw new Error(job.error_message || "플롯 생성 실패");
      }
      const plotText =
        (job.output_payload && job.output_payload.plot_text) ||
        JSON.stringify(job.output_payload || {}, null, 2);
      const safe = escapeHtml(plotText);
      appendAIHtml(
        '<p>스토리보드(JSON) 결과입니다.</p><pre class="resultJson" style="white-space:pre-wrap;font-size:12px;max-height:240px;overflow:auto">' +
          safe +
          "</pre>"
      );
    });
  }

  function handleImageApi(text) {
    return window.BugSiteApi.ensureAuth().then(function () {
      const pid = sessionStorage.getItem("bug_project_id");
      if (!pid) throw new Error("먼저 스토리보드 단계에서 프로젝트를 만들어 주세요.");
      return window.BugSiteApi.createTextToImageJob(pid, text);
    }).then(function (job) {
      return window.BugSiteApi.pollJob(job.id).then(function (done) {
        return { done: done, jobId: job.id };
      });
    }).then(function (x) {
      if (x.done.status === "failed") {
        throw new Error(x.done.error_message || "이미지 생성 실패");
      }
      return window.BugSiteApi.fetchJobOutputs(x.jobId);
    }).then(function (out) {
      if (!out || !out.outputs || !out.outputs.length) {
        appendAI("이미지 생성이 완료되었습니다. 작업 상세에서 URL을 확인하세요.");
        return;
      }
      const first = out.outputs[0];
      const url = first.url || "";
      if (url) {
        appendAIHtml(
          '<p>생성 이미지</p><p><img src="' +
            escapeHtml(url) +
            '" alt="" style="max-width:100%;border-radius:8px" /></p>'
        );
      } else {
        appendAI("이미지가 생성되었습니다.");
      }
    });
  }

  function handleVideoApi(text) {
    return window.BugSiteApi.ensureAuth().then(function () {
      const pid = sessionStorage.getItem("bug_project_id");
      if (!pid) throw new Error("먼저 스토리보드 단계에서 프로젝트를 만들어 주세요.");
      return window.BugSiteApi.createTextToImageToVideoJob(pid, text);
    }).then(function (job) {
      return window.BugSiteApi.pollJob(job.id, { interval: 2000, maxAttempts: 400 }).then(function (done) {
        return { done: done, jobId: job.id };
      });
    }).then(function (x) {
      if (x.done.status === "failed") {
        throw new Error(x.done.error_message || "영상 생성 실패");
      }
      return window.BugSiteApi.fetchJobOutputs(x.jobId);
    }).then(function (out) {
      if (!out || !out.outputs || !out.outputs.length) {
        appendAI("영상(또는 GIF) 생성이 완료되었습니다.");
        return;
      }
      const lines = out.outputs
        .map(function (o) {
          const u = o.url || "";
          if (!u) return "";
          const ct = (o.content_type || "").toLowerCase();
          const isGif = ct.indexOf("gif") !== -1 || /\.gif(\?|$)/i.test(u);
          if (isGif) {
            return '<p><img src="' + escapeHtml(u) + '" alt="" style="max-width:100%;border-radius:8px" /></p>';
          }
          const t = o.media_type || "";
          if (t === "video") {
            return '<p><video src="' +
              escapeHtml(u) +
              '" controls style="max-width:100%;border-radius:8px"></video></p>';
          }
          return '<p><img src="' + escapeHtml(u) + '" alt="" style="max-width:100%;border-radius:8px" /></p>';
        })
        .join("");
      appendAIHtml("<p>생성 결과</p>" + (lines || "<p>파일이 저장되었습니다.</p>"));
    });
  }

  send.addEventListener("click", function () {
    const text = msg.value.trim();
    if (!text) return;
    appendMe(text);
    msg.value = "";
    autosize(msg);

    if (!window.BugSiteApi) {
      window.setTimeout(function () {
        if (currentStep === "storyboard") {
          appendAI("좋아. 스토리보드를 ‘수정’할까, 아니면 ‘확정’해서 이미지 단계로 넘어갈까?");
        } else if (currentStep === "image") {
          appendAI("원하는 이미지 스타일(실사/3D/일러스트)과 분위기 키워드를 3개만 줘.");
        } else {
          appendAI("영상 템포(빠르게/보통/느리게)와 자막 유무를 알려줘. 그다음 렌더링을 시작할게.");
        }
      }, 350);
      return;
    }

    window.setTimeout(function () {
      const run =
        currentStep === "storyboard"
          ? handleStoryboardApi(text)
          : currentStep === "image"
            ? handleImageApi(text)
            : handleVideoApi(text);
      run.catch(function (err) {
        appendAI("오류: " + (err && err.message ? err.message : String(err)));
      });
    }, 200);
  });

  msg.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send.click();
    }
  });

  document.querySelectorAll("[data-q]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      msg.value = (msg.value + " " + btn.dataset.q).trim();
      autosize(msg);
      msg.focus();
    });
  });

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      setStep(chip.dataset.step);
    });
  });

  const reviseStoryboardBtn = document.getElementById("reviseStoryboardBtn");
  const confirmStoryboardBtn = document.getElementById("confirmStoryboardBtn");

  if (reviseStoryboardBtn) {
    reviseStoryboardBtn.addEventListener("click", function () {
      appendMe("수정: 1컷은 제품 클로즈업 대신, 매장 입구 간판으로 시작해줘.");
      window.setTimeout(function () {
        appendAI("좋아. 오프닝을 ‘매장 간판→주문→제조→완성’ 흐름으로 바꿔볼게.");
      }, 300);
    });
  }

  if (confirmStoryboardBtn) {
    confirmStoryboardBtn.addEventListener("click", function () {
      setStep("image");
      appendMe("확정!");
      window.setTimeout(function () {
        appendAI("이미지 단계로 넘어갈게. 각 컷의 스타일을 정하자: 실사/3D/일러스트 중 뭐가 좋아?");
      }, 300);
    });
  }

  function updateExportState() {
    if (!exportBtn) return;
    exportBtn.disabled = currentStep !== "video";
    exportBtn.classList.toggle("primary", currentStep === "video");
  }

  updateExportState();
  chips.forEach(function (c) {
    c.addEventListener("click", updateExportState);
  });
  if (confirmStoryboardBtn) confirmStoryboardBtn.addEventListener("click", updateExportState);
})();

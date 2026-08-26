function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

var state = {
  keywords: 'Software Engineer',
  location: 'India',
  remote: '',
  job_type: '',
  experience_level: '',
  date_posted: '',
  exclude_service_companies: false,
  top_tier_only: false,
  page: 1,
  limit: 35,
  jobs: [],
  posts: [],
  selectedJob: null,
  currentView: 'jobs',
  bookmarks: JSON.parse(localStorage.getItem('saved_jobs') || '[]'),
  resumeProfile: JSON.parse(localStorage.getItem('resume_profile') || 'null'),
  isLoading: false,
  activeApplySessionId: null,
  applyPollingTimer: null
};

function safeCreateIcons() {
  try { if (window.lucide && typeof window.lucide.createIcons === 'function') window.lucide.createIcons(); } catch(e){}
}

var searchForm, keywordInput, locationInput, filterExp, filterJobType, excludeServiceCheck, topTierOnlyCheck, quickTierTopBtn, resetFiltersBtn;
var jobCardsContainer, jobDetailsPane, resultCountText, searchQuerySummary, sourceBadge;
var prevPageBtn, nextPageBtn, paginationIndicator, bookmarkCount, modalBookmarkCount;
var bookmarksModal, openBookmarksBtn, closeBookmarksBtn, doneBookmarksBtn, clearBookmarksBtn, bookmarksList;
var statsModal, openStatsBtn, closeStatsBtn, exportCsvBtn, exportJsonBtn, themeToggle;
var openResumeBtn, resumeModal, closeResumeModalBtn, resumeTabFileBtn, resumeTabTextBtn;
var resumeFileSection, resumeTextSection, resumeFileInput, resumeTextInput, processResumeBtn, selectedFileName;
var activeResumeBanner, resumeBannerTitle, resumeBannerSkills, resumeAutoSearchBtn, clearResumeBtn, resumeBtnText;
var coverLetterModal, closeCoverLetterBtn, doneCoverLetterBtn, coverLetterText, copyCoverLetterBtn;

// Auto-Apply Elements
var autoApplyModal, closeAutoApplyModalBtn, doneAutoApplyBtn, autoApplyJobTitle, autoApplyCompany, autoApplyStatusBadge, autoApplyLogs;
var autoApplyQuestionCard, promptQuestionText, promptAnswerInput, submitPromptAnswerBtn;
var openAutoApplySettingsBtn, autoApplySettingsModal, closeAutoApplySettingsBtn, autoApplyProfileForm;
var profFullName, profEmail, profPhone, profCity, profNotice, profCurrentCtc, profExpectedCtc, profLinkedin, profGithub, profAuth;

// Recruiter Posts & Cold Email Elements
var viewJobsTabBtn, viewPostsTabBtn, jobsMainSection, postsViewSection, postsCardsContainer, postsCountBadge;
var coldEmailModal, closeColdEmailBtn, doneColdEmailBtn, copyColdEmailBtn, copyRecipientEmailBtn, coldEmailRecipient, coldEmailSubject, coldEmailBody, coldEmailTitle, coldEmailSubtitle;

document.addEventListener('DOMContentLoaded', function() {
  searchForm = document.getElementById('searchForm');
  keywordInput = document.getElementById('keywordInput');
  locationInput = document.getElementById('locationInput');
  filterExp = document.getElementById('filterExp');
  filterJobType = document.getElementById('filterJobType');
  excludeServiceCheck = document.getElementById('excludeServiceCheck');
  resetFiltersBtn = document.getElementById('resetFiltersBtn');
  jobCardsContainer = document.getElementById('jobCardsContainer');
  jobDetailsPane = document.getElementById('jobDetailsPane');
  resultCountText = document.getElementById('resultCountText');
  searchQuerySummary = document.getElementById('searchQuerySummary');
  sourceBadge = document.getElementById('sourceBadge');
  prevPageBtn = document.getElementById('prevPageBtn');
  nextPageBtn = document.getElementById('nextPageBtn');
  paginationIndicator = document.getElementById('paginationIndicator');
  bookmarkCount = document.getElementById('bookmarkCount');
  modalBookmarkCount = document.getElementById('modalBookmarkCount');
  bookmarksModal = document.getElementById('bookmarksModal');
  openBookmarksBtn = document.getElementById('openBookmarksBtn');
  closeBookmarksBtn = document.getElementById('closeBookmarksBtn');
  doneBookmarksBtn = document.getElementById('doneBookmarksBtn');
  clearBookmarksBtn = document.getElementById('clearBookmarksBtn');
  bookmarksList = document.getElementById('bookmarksList');
  statsModal = document.getElementById('statsModal');
  openStatsBtn = document.getElementById('openStatsBtn');
  closeStatsBtn = document.getElementById('closeStatsBtn');
  exportCsvBtn = document.getElementById('exportCsvBtn');
  exportJsonBtn = document.getElementById('exportJsonBtn');
  themeToggle = document.getElementById('themeToggle');
  openResumeBtn = document.getElementById('openResumeBtn');
  resumeModal = document.getElementById('resumeModal');
  closeResumeModalBtn = document.getElementById('closeResumeModalBtn');
  resumeTabFileBtn = document.getElementById('resumeTabFileBtn');
  resumeTabTextBtn = document.getElementById('resumeTabTextBtn');
  resumeFileSection = document.getElementById('resumeFileSection');
  resumeTextSection = document.getElementById('resumeTextSection');
  resumeFileInput = document.getElementById('resumeFileInput');
  resumeTextInput = document.getElementById('resumeTextInput');
  processResumeBtn = document.getElementById('processResumeBtn');
  selectedFileName = document.getElementById('selectedFileName');
  activeResumeBanner = document.getElementById('activeResumeBanner');
  resumeBannerTitle = document.getElementById('resumeBannerTitle');
  resumeBannerSkills = document.getElementById('resumeBannerSkills');
  resumeAutoSearchBtn = document.getElementById('resumeAutoSearchBtn');
  clearResumeBtn = document.getElementById('clearResumeBtn');
  resumeBtnText = document.getElementById('resumeBtnText');
  coverLetterModal = document.getElementById('coverLetterModal');
  closeCoverLetterBtn = document.getElementById('closeCoverLetterBtn');
  doneCoverLetterBtn = document.getElementById('doneCoverLetterBtn');
  coverLetterText = document.getElementById('coverLetterText');
  copyCoverLetterBtn = document.getElementById('copyCoverLetterBtn');

  // Auto-Apply Elements
  autoApplyModal = document.getElementById('autoApplyModal');
  closeAutoApplyModalBtn = document.getElementById('closeAutoApplyModalBtn');
  doneAutoApplyBtn = document.getElementById('doneAutoApplyBtn');
  autoApplyJobTitle = document.getElementById('autoApplyJobTitle');
  autoApplyCompany = document.getElementById('autoApplyCompany');
  autoApplyStatusBadge = document.getElementById('autoApplyStatusBadge');
  autoApplyLogs = document.getElementById('autoApplyLogs');
  autoApplyQuestionCard = document.getElementById('autoApplyQuestionCard');
  promptQuestionText = document.getElementById('promptQuestionText');
  promptAnswerInput = document.getElementById('promptAnswerInput');
  submitPromptAnswerBtn = document.getElementById('submitPromptAnswerBtn');

  openAutoApplySettingsBtn = document.getElementById('openAutoApplySettingsBtn');
  autoApplySettingsModal = document.getElementById('autoApplySettingsModal');
  closeAutoApplySettingsBtn = document.getElementById('closeAutoApplySettingsBtn');
  autoApplyProfileForm = document.getElementById('autoApplyProfileForm');
  profFullName = document.getElementById('profFullName');
  profEmail = document.getElementById('profEmail');
  profPhone = document.getElementById('profPhone');
  profCity = document.getElementById('profCity');
  profNotice = document.getElementById('profNotice');
  profCurrentCtc = document.getElementById('profCurrentCtc');
  profExpectedCtc = document.getElementById('profExpectedCtc');
  profLinkedin = document.getElementById('profLinkedin');
  profGithub = document.getElementById('profGithub');
  profAuth = document.getElementById('profAuth');

  initTheme();
  updateBookmarkUI();
  updateResumeUI();
  setupEventListeners();

  // Load default search for Software Engineer in India
  if (state.resumeProfile && state.resumeProfile.search_queries && state.resumeProfile.search_queries.length) {
    var topQuery = state.resumeProfile.search_queries[0];
    if (keywordInput) keywordInput.value = topQuery;
    if (locationInput) locationInput.value = 'India';
    state.keywords = topQuery;
    state.location = 'India';
  } else {
    if (keywordInput) keywordInput.value = 'Software Engineer';
    if (locationInput) locationInput.value = 'India';
    state.keywords = 'Software Engineer';
    state.location = 'India';
  }

  fetchJobs();
});

function initTheme() {
  var isDark = localStorage.getItem('theme') === 'dark' ||
    (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
  if (isDark) document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');
}

function toggleTheme() {
  var isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  safeCreateIcons();
}

function setupEventListeners() {
  if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

  if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault();
      state.keywords = keywordInput ? keywordInput.value.trim() : 'Software Engineer';
      state.location = locationInput ? locationInput.value.trim() : 'India';
      state.page = 1;
      fetchJobs();
    });
  }

  if (jobCardsContainer) {
    jobCardsContainer.addEventListener('click', function(e) {
      var bookmarkBtn = e.target.closest('[data-bookmark-id]');
      if (bookmarkBtn) {
        e.stopPropagation();
        toggleBookmark(bookmarkBtn.getAttribute('data-bookmark-id'));
        return;
      }
      var card = e.target.closest('[data-job-id]');
      if (card) selectJob(card.getAttribute('data-job-id'));
    });
  }

  document.querySelectorAll('input[name="filterRemote"]').forEach(function(r) {
    r.addEventListener('change', function(e) { state.remote = e.target.value; state.page = 1; fetchJobs(); });
  });
  document.querySelectorAll('input[name="filterDate"]').forEach(function(r) {
    r.addEventListener('change', function(e) { state.date_posted = e.target.value; state.page = 1; fetchJobs(); });
  });
  if (filterExp) filterExp.addEventListener('change', function(e) { state.experience_level = e.target.value; state.page = 1; fetchJobs(); });
  if (filterJobType) filterJobType.addEventListener('change', function(e) { state.job_type = e.target.value; state.page = 1; fetchJobs(); });

  if (excludeServiceCheck) {
    excludeServiceCheck.addEventListener('change', function(e) {
      state.exclude_service_companies = e.target.checked;
      state.page = 1;
      fetchJobs();
    });
  }

  topTierOnlyCheck = document.getElementById('topTierOnlyCheck');
  quickTierTopBtn = document.getElementById('quickTierTopBtn');

  if (topTierOnlyCheck) {
    topTierOnlyCheck.addEventListener('change', function(e) {
      state.top_tier_only = e.target.checked;
      state.page = 1;
      fetchJobs();
    });
  }

  if (quickTierTopBtn) {
    quickTierTopBtn.addEventListener('click', function() {
      if (topTierOnlyCheck) {
        topTierOnlyCheck.checked = !topTierOnlyCheck.checked;
        state.top_tier_only = topTierOnlyCheck.checked;
      } else {
        state.top_tier_only = !state.top_tier_only;
      }
      state.page = 1;
      fetchJobs();
    });
  }

  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', function() {
      if (keywordInput) keywordInput.value = 'Software Engineer';
      if (locationInput) locationInput.value = 'India';
      state.keywords = 'Software Engineer';
      state.location = 'India';
      state.remote = '';
      state.date_posted = '';
      state.experience_level = '';
      state.job_type = '';
      state.exclude_service_companies = false;
      state.top_tier_only = false;
      state.page = 1;
      var defRem = document.querySelector('input[name="filterRemote"][value=""]');
      if (defRem) defRem.checked = true;
      var defDate = document.querySelector('input[name="filterDate"][value=""]');
      if (defDate) defDate.checked = true;
      if (filterExp) filterExp.value = '';
      if (filterJobType) filterJobType.value = '';
      if (excludeServiceCheck) excludeServiceCheck.checked = false;
      if (topTierOnlyCheck) topTierOnlyCheck.checked = false;
      fetchJobs();
    });
  }

  document.querySelectorAll('.quick-tag').forEach(function(tag) {
    tag.addEventListener('click', function() {
      if (keywordInput) keywordInput.value = tag.innerText.trim();
      state.keywords = tag.innerText.trim();
      state.page = 1;
      fetchJobs();
    });
  });

  if (prevPageBtn) prevPageBtn.addEventListener('click', function() {
    if (state.page > 1) { state.page--; fetchJobs(); }
  });
  if (nextPageBtn) nextPageBtn.addEventListener('click', function() {
    state.page++; fetchJobs();
  });

  if (openBookmarksBtn) openBookmarksBtn.addEventListener('click', function() {
    renderBookmarksModal();
    bookmarksModal.classList.remove('hidden');
    bookmarksModal.classList.add('flex');
    safeCreateIcons();
  });
  if (closeBookmarksBtn) closeBookmarksBtn.addEventListener('click', function() {
    bookmarksModal.classList.add('hidden'); bookmarksModal.classList.remove('flex');
  });
  if (doneBookmarksBtn) doneBookmarksBtn.addEventListener('click', function() {
    bookmarksModal.classList.add('hidden'); bookmarksModal.classList.remove('flex');
  });
  if (clearBookmarksBtn) clearBookmarksBtn.addEventListener('click', function() {
    if (confirm('Clear all saved jobs?')) {
      state.bookmarks = [];
      localStorage.setItem('saved_jobs', JSON.stringify([]));
      updateBookmarkUI(); renderBookmarksModal(); renderJobsList();
    }
  });

  if (openStatsBtn) openStatsBtn.addEventListener('click', fetchAndShowStats);
  if (closeStatsBtn) closeStatsBtn.addEventListener('click', function() {
    statsModal.classList.add('hidden'); statsModal.classList.remove('flex');
  });

  if (openResumeBtn) openResumeBtn.addEventListener('click', function() {
    resumeModal.classList.remove('hidden');
    resumeModal.classList.add('flex');
    safeCreateIcons();
  });
  if (closeResumeModalBtn) closeResumeModalBtn.addEventListener('click', function() {
    resumeModal.classList.add('hidden'); resumeModal.classList.remove('flex');
  });

  if (resumeTabFileBtn && resumeTabTextBtn) {
    resumeTabFileBtn.addEventListener('click', function() {
      resumeTabFileBtn.className = 'pb-2.5 px-4 font-bold border-b-2 border-brand-500 text-brand-600 dark:text-brand-400';
      resumeTabTextBtn.className = 'pb-2.5 px-4 font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-800';
      resumeFileSection.classList.remove('hidden'); resumeTextSection.classList.add('hidden');
    });
    resumeTabTextBtn.addEventListener('click', function() {
      resumeTabTextBtn.className = 'pb-2.5 px-4 font-bold border-b-2 border-brand-500 text-brand-600 dark:text-brand-400';
      resumeTabFileBtn.className = 'pb-2.5 px-4 font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-800';
      resumeTextSection.classList.remove('hidden'); resumeFileSection.classList.add('hidden');
    });
  }

  if (resumeFileInput) {
    resumeFileInput.addEventListener('change', function(e) {
      if (e.target.files && e.target.files[0]) {
        selectedFileName.innerText = 'Selected: ' + e.target.files[0].name;
        selectedFileName.classList.remove('hidden');
      }
    });
  }

  if (processResumeBtn) processResumeBtn.addEventListener('click', handleProcessResume);

  if (clearResumeBtn) {
    clearResumeBtn.addEventListener('click', function() {
      state.resumeProfile = null;
      localStorage.removeItem('resume_profile');
      updateResumeUI();
      if (keywordInput) keywordInput.value = 'Software Engineer';
      if (locationInput) locationInput.value = 'India';
      state.keywords = 'Software Engineer';
      state.location = 'India';
      fetchJobs();
    });
  }

  if (resumeAutoSearchBtn) {
    resumeAutoSearchBtn.addEventListener('click', function() {
      if (state.resumeProfile && state.resumeProfile.search_queries && state.resumeProfile.search_queries.length) {
        keywordInput.value = state.resumeProfile.search_queries[0];
        locationInput.value = 'India';
        state.keywords = state.resumeProfile.search_queries[0];
        state.location = 'India';
        state.page = 1;
        fetchJobs();
      }
    });
  }

  if (closeCoverLetterBtn) closeCoverLetterBtn.addEventListener('click', function() {
    coverLetterModal.classList.add('hidden'); coverLetterModal.classList.remove('flex');
  });
  if (doneCoverLetterBtn) doneCoverLetterBtn.addEventListener('click', function() {
    coverLetterModal.classList.add('hidden'); coverLetterModal.classList.remove('flex');
  });
  if (copyCoverLetterBtn) copyCoverLetterBtn.addEventListener('click', function() {
    navigator.clipboard.writeText(coverLetterText.value);
    showToast('Cover letter copied!');
  });

  if (exportCsvBtn) exportCsvBtn.addEventListener('click', function() {
    var p = new URLSearchParams({
      keywords: state.keywords,
      location: state.location,
      exclude_service_companies: state.exclude_service_companies,
      format: 'csv'
    });
    window.open('/api/export?' + p.toString(), '_blank');
  });
  if (exportJsonBtn) exportJsonBtn.addEventListener('click', function() {
    var p = new URLSearchParams({
      keywords: state.keywords,
      location: state.location,
      exclude_service_companies: state.exclude_service_companies,
      format: 'json'
    });
    window.open('/api/export?' + p.toString(), '_blank');
  });

  // Auto-Apply Modal Listeners
  if (closeAutoApplyModalBtn) closeAutoApplyModalBtn.addEventListener('click', function() {
    autoApplyModal.classList.add('hidden'); autoApplyModal.classList.remove('flex');
    if (state.applyPollingTimer) clearInterval(state.applyPollingTimer);
  });
  if (doneAutoApplyBtn) doneAutoApplyBtn.addEventListener('click', function() {
    autoApplyModal.classList.add('hidden'); autoApplyModal.classList.remove('flex');
    if (state.applyPollingTimer) clearInterval(state.applyPollingTimer);
  });

  if (submitPromptAnswerBtn) {
    submitPromptAnswerBtn.addEventListener('click', submitUserPromptAnswer);
  }
  if (promptAnswerInput) {
    promptAnswerInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') submitUserPromptAnswer();
    });
  }

  // Auto-Apply Profile Config Listeners
  if (openAutoApplySettingsBtn) openAutoApplySettingsBtn.addEventListener('click', loadAndOpenAutoApplySettings);
  if (closeAutoApplySettingsBtn) closeAutoApplySettingsBtn.addEventListener('click', function() {
    autoApplySettingsModal.classList.add('hidden'); autoApplySettingsModal.classList.remove('flex');
  });
  if (autoApplyProfileForm) autoApplyProfileForm.addEventListener('submit', handleSaveAutoApplyProfile);

  // View Switcher Tabs
  viewJobsTabBtn = document.getElementById('viewJobsTabBtn');
  viewPostsTabBtn = document.getElementById('viewPostsTabBtn');
  jobsMainSection = document.getElementById('jobsMainSection');
  postsViewSection = document.getElementById('postsViewSection');
  postsCardsContainer = document.getElementById('postsCardsContainer');
  postsCountBadge = document.getElementById('postsCountBadge');

  if (viewJobsTabBtn) {
    viewJobsTabBtn.addEventListener('click', function() {
      switchView('jobs');
    });
  }

  if (viewPostsTabBtn) {
    viewPostsTabBtn.addEventListener('click', function() {
      switchView('posts');
    });
  }

  // Cold Email Modal Listeners
  coldEmailModal = document.getElementById('coldEmailModal');
  closeColdEmailBtn = document.getElementById('closeColdEmailBtn');
  doneColdEmailBtn = document.getElementById('doneColdEmailBtn');
  copyColdEmailBtn = document.getElementById('copyColdEmailBtn');
  copyRecipientEmailBtn = document.getElementById('copyRecipientEmailBtn');
  coldEmailRecipient = document.getElementById('coldEmailRecipient');
  coldEmailSubject = document.getElementById('coldEmailSubject');
  coldEmailBody = document.getElementById('coldEmailBody');
  coldEmailTitle = document.getElementById('coldEmailTitle');
  coldEmailSubtitle = document.getElementById('coldEmailSubtitle');

  if (closeColdEmailBtn) closeColdEmailBtn.addEventListener('click', function() {
    coldEmailModal.classList.add('hidden'); coldEmailModal.classList.remove('flex');
  });
  if (doneColdEmailBtn) doneColdEmailBtn.addEventListener('click', function() {
    coldEmailModal.classList.add('hidden'); coldEmailModal.classList.remove('flex');
  });
  if (copyColdEmailBtn) {
    copyColdEmailBtn.addEventListener('click', function() {
      if (coldEmailBody) {
        navigator.clipboard.writeText(coldEmailBody.value)
          .then(function() { showToast('✅ Cold email copied to clipboard!'); })
          .catch(function() { showToast('Copied'); });
      }
    });
  }
  if (copyRecipientEmailBtn) {
    copyRecipientEmailBtn.addEventListener('click', function() {
      if (coldEmailRecipient) {
        navigator.clipboard.writeText(coldEmailRecipient.value)
          .then(function() { showToast('✅ Recruiter email copied: ' + coldEmailRecipient.value); })
          .catch(function() { showToast('Copied'); });
      }
    });
  }
}

function handleProcessResume() {
  var isFileTab = !resumeFileSection.classList.contains('hidden');
  processResumeBtn.disabled = true;
  processResumeBtn.innerText = 'Analyzing...';

  var promise;
  if (isFileTab) {
    var file = resumeFileInput.files[0];
    if (!file) { alert('Please select a file.'); processResumeBtn.disabled = false; processResumeBtn.innerText = 'Analyze Resume'; return; }
    var fd = new FormData(); fd.append('file', file);
    promise = fetch('/api/resume/parse-file', { method: 'POST', body: fd });
  } else {
    var txt = resumeTextInput.value.trim();
    if (!txt) { alert('Please paste text.'); processResumeBtn.disabled = false; processResumeBtn.innerText = 'Analyze Resume'; return; }
    promise = fetch('/api/resume/parse-text', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: txt }) });
  }

  promise.then(function(res) {
    if (!res.ok) throw new Error('Parse failed');
    return res.json();
  }).then(function(profileData) {
    state.resumeProfile = profileData;
    localStorage.setItem('resume_profile', JSON.stringify(profileData));
    updateResumeUI();
    resumeModal.classList.add('hidden');
    resumeModal.classList.remove('flex');
    showToast('Resume analyzed! ' + profileData.skills.length + ' skills detected');
    if (profileData.search_queries && profileData.search_queries.length) {
      keywordInput.value = profileData.search_queries[0];
      state.keywords = profileData.search_queries[0];
      state.page = 1;
      fetchJobs();
    } else {
      renderJobsList();
    }
  }).catch(function(err) {
    alert('Resume parsing error: ' + err.message);
  }).finally(function() {
    processResumeBtn.disabled = false;
    processResumeBtn.innerText = 'Analyze Resume & Enable Auto-Apply';
    safeCreateIcons();
  });
}

function updateResumeUI() {
  if (state.resumeProfile) {
    if (activeResumeBanner) activeResumeBanner.classList.remove('hidden');
    if (resumeBannerTitle) resumeBannerTitle.innerText = (state.resumeProfile.candidate_title || 'Candidate') + ' (' + (state.resumeProfile.experience_years || 3) + '+ yrs)';
    if (resumeBannerSkills) {
      var sk = (state.resumeProfile.skills || []).slice(0, 7).join(', ');
      resumeBannerSkills.innerText = 'Skills: ' + (sk || 'General');
    }
    if (resumeBtnText) resumeBtnText.innerText = 'Resume Active';
  } else {
    if (activeResumeBanner) activeResumeBanner.classList.add('hidden');
    if (resumeBtnText) resumeBtnText.innerText = 'Upload Resume';
  }
}

function computeMatchForJob(job) {
  if (!state.resumeProfile || !state.resumeProfile.skills) return null;
  var candidateSkills = (state.resumeProfile.skills || []).map(function(s) { return s.toLowerCase(); });
  var jobText = ((job.title || '') + ' ' + (job.description || '') + ' ' + (job.skills || []).join(' ')).toLowerCase();
  var matched = [];
  candidateSkills.forEach(function(s) { if (jobText.indexOf(s) >= 0) matched.push(s); });
  var base = Math.min(60, matched.length * 9);
  var titleBonus = (job.title || '').toLowerCase().indexOf((state.resumeProfile.candidate_title || '').toLowerCase()) >= 0 ? 25 : 15;
  var score = Math.min(98, Math.max(matched.length ? 60 : 40, base + titleBonus + 14));
  return { score: score, matchedCount: matched.length, matchedSkills: matched.slice(0, 6) };
}

function fetchJobs() {
  state.isLoading = true;
  if (jobCardsContainer) {
    jobCardsContainer.innerHTML = '<div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3"><div class="flex items-center space-x-3"><div class="w-11 h-11 rounded-xl skeleton shrink-0"></div><div class="flex-1 space-y-2"><div class="h-4 skeleton rounded-md w-3/4"></div><div class="h-3 skeleton rounded-md w-1/2"></div></div></div></div>';
  }

  var p = new URLSearchParams({
    keywords: state.keywords || 'Software Engineer',
    location: state.location || 'India',
    page: state.page,
    limit: state.limit,
    exclude_service_companies: state.exclude_service_companies
  });
  if (state.top_tier_only) p.append('top_tier_only', 'true');
  if (state.remote) p.append('remote', state.remote);
  if (state.job_type) p.append('job_type', state.job_type);
  if (state.experience_level) p.append('experience_level', state.experience_level);
  if (state.date_posted) p.append('date_posted', state.date_posted);

  fetch('/api/jobs/search?' + p.toString())
    .then(function(res) { return res.json(); })
    .then(function(data) {
      state.jobs = data.jobs || [];
      if (resultCountText) resultCountText.innerText = (data.total_count || state.jobs.length) + ' Opportunities in India';
      var terms = [state.keywords, state.location].filter(Boolean).join(' in ') || 'Software Engineer in India';
      if (searchQuerySummary) searchQuerySummary.innerText = 'Search: "' + terms + '" - Page ' + state.page;

      if (sourceBadge) {
        if (data.source === 'live') {
          sourceBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span> Live LinkedIn India';
          sourceBadge.className = 'text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800 flex items-center';
        } else {
          sourceBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-blue-500 mr-1.5"></span> Smart Index';
          sourceBadge.className = 'text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 border border-blue-300 dark:border-blue-800 flex items-center';
        }
      }
      if (paginationIndicator) paginationIndicator.innerText = 'Page ' + state.page;
      if (prevPageBtn) prevPageBtn.disabled = state.page <= 1;
      if (nextPageBtn) nextPageBtn.disabled = state.jobs.length === 0;

      renderJobsList();
      if (state.jobs.length > 0) selectJob(state.jobs[0].id);
    })
    .catch(function(err) {
      console.error('Fetch error', err);
      if (resultCountText) resultCountText.innerText = 'Unable to load jobs';
    })
    .finally(function() { state.isLoading = false; });
}

function renderJobsList() {
  if (!jobCardsContainer) return;
  if (!state.jobs.length) {
    jobCardsContainer.innerHTML = '<div class="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 text-center space-y-3"><h3 class="font-bold text-slate-900 dark:text-white">No matching job openings found</h3><p class="text-xs text-slate-500">Try loosening your search keywords or unchecking filters.</p></div>';
    return;
  }

  var html = '';
  for (var i = 0; i < state.jobs.length; i++) {
    var job = state.jobs[i];
    var isSelected = state.selectedJob && String(state.selectedJob.id) === String(job.id);
    var isSaved = state.bookmarks.some(function(b) { return String(b.id) === String(job.id); });
    var cId = escapeHtml(job.id);
    var cTitle = escapeHtml(job.title);
    var cCompany = escapeHtml(job.company_name);
    var cLoc = escapeHtml(job.location);
    var cSalary = escapeHtml(job.salary || 'Competitive');
    var isExactSalary = job.salary_type === 'exact';
    var isLeetCodeVerified = job.salary_type === 'leetcode_verified';
    var cWorkplace = escapeHtml(job.workplace_type);
    var cPosted = escapeHtml(job.posted_time);
    var fallback = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(job.company_name || 'J') + '&background=0a66c2&color=fff&size=48';
    var logo = job.company_logo || fallback;
    var match = computeMatchForJob(job);

    var selectedClass = isSelected
      ? 'bg-brand-50/70 dark:bg-brand-500/10 border-brand-500 ring-2 ring-brand-500/30'
      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 shadow-sm';

    var matchBadge = '';
    if (match) {
      var matchClass = match.score >= 80
        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
        : 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300';
      matchBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold ' + matchClass + '">' + match.score + '% Match</span>';
    }

    var bookmarkClass = isSaved ? 'text-amber-500 fill-amber-500' : '';
    var wpClass = cWorkplace === 'Remote'
      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
      : cWorkplace === 'Hybrid'
      ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300'
      : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';

    var topTierBadge = job.is_top_tier
      ? '<span class="px-2 py-0.5 rounded-md font-black bg-gradient-to-r from-amber-100 to-indigo-100 text-amber-900 dark:from-amber-950 dark:to-indigo-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800/80 shadow-xs" title="⭐ Tier-1 High-Pay Employer (30+ LPA)">⭐ 30+ LPA</span>'
      : '';

    var salaryBadge = '';
    if (isExactSalary) {
      salaryBadge = '<span class="px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-300 dark:border-emerald-800 flex items-center gap-1" title="Scraped directly from employer posting">💰 ' + cSalary + '</span>';
    } else if (isLeetCodeVerified) {
      salaryBadge = '<span class="px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-300 dark:border-indigo-800 flex items-center gap-1" title="Crowdsourced LeetCode &amp; Levels.fyi verified compensation">⚡ ' + cSalary + '</span>';
    } else {
      salaryBadge = '<span class="px-2 py-0.5 rounded-md bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 font-medium border border-amber-200/60 dark:border-amber-800/60" title="Indian Tech Market compensation benchmark">📊 ' + cSalary + '</span>';
    }

    var serviceBadge = (job.is_service_company && !state.exclude_service_companies)
      ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400 font-semibold border border-rose-200 dark:border-rose-800">IT Services</span>'
      : '';

    html += '<div data-job-id="' + cId + '" class="job-card-transition p-4 rounded-2xl border cursor-pointer ' + selectedClass + '">'
      + '<div class="flex items-start justify-between gap-3">'
      + '<div class="w-11 h-11 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center overflow-hidden shrink-0">'
      + '<img src="' + escapeHtml(logo) + '" alt="' + cCompany + '" class="w-full h-full object-cover" onerror="this.onerror=null;this.src=\'' + fallback + '\';" />'
      + '</div>'
      + '<div class="flex-1 min-w-0">'
      + '<h3 class="font-bold text-sm sm:text-base text-slate-900 dark:text-white truncate" title="' + cTitle + '">' + cTitle + '</h3>'
      + '<p class="text-xs text-slate-600 dark:text-slate-400 font-medium truncate mt-0.5">' + cCompany + ' &middot; <span class="text-slate-500">' + cLoc + '</span></p>'
      + '</div>'
      + '<div class="flex items-center space-x-1.5 shrink-0">'
      + matchBadge
      + '<button data-bookmark-id="' + cId + '" class="p-1.5 rounded-lg text-slate-400 hover:text-amber-500 transition"><i data-lucide="bookmark" class="w-4 h-4 ' + bookmarkClass + '"></i></button>'
      + '</div>'
      + '</div>'
      + '<div class="mt-3 flex flex-wrap items-center gap-1.5 text-[11px]">'
      + '<span class="px-2 py-0.5 rounded-md font-semibold ' + wpClass + '">' + cWorkplace + '</span>'
      + topTierBadge
      + '<span class="px-2 py-0.5 rounded-md font-semibold bg-indigo-50/80 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60">🎯 ' + escapeHtml(job.experience_required || '2–4 Yrs') + '</span>'
      + salaryBadge
      + serviceBadge
      + '<span class="text-slate-400 dark:text-slate-500 ml-auto">' + cPosted + '</span>'
      + '</div>'
      + '</div>';
  }
  jobCardsContainer.innerHTML = html;
  safeCreateIcons();
}

function selectJob(jobId) {
  var job = state.jobs.find(function(j) { return String(j.id) === String(jobId); });
  if (!job) job = state.bookmarks.find(function(b) { return String(b.id) === String(jobId); });
  if (!job || !jobDetailsPane) return;
  state.selectedJob = job;
  renderJobsList();

  jobDetailsPane.innerHTML = '<div class="space-y-4 p-4"><div class="h-5 skeleton rounded-md w-3/4"></div><div class="h-4 skeleton rounded-md w-1/2"></div></div>';

  fetch('/api/jobs/' + jobId)
    .then(function(res) { return res.json(); })
    .then(function(details) { renderJobDetails(job, details); })
    .catch(function() { renderJobDetails(job, null); });
}

function renderJobDetails(job, fullDetails) {
  if (!jobDetailsPane) return;
  var isSaved = state.bookmarks.some(function(b) { return String(b.id) === String(job.id); });
  var desc = (fullDetails && fullDetails.description_html) ? fullDetails.description_html : '<div>' + escapeHtml(job.description || '').replace(/\n/g, '<br>') + '</div>';
  var applyUrl = job.linkedin_url || ('https://www.linkedin.com/jobs/view/' + job.id);
  var fallback = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(job.company_name || 'J') + '&background=0a66c2&color=fff&size=64';
  var logo = job.company_logo || fallback;
  var match = computeMatchForJob(job);

  var salaryDisplay = (fullDetails && fullDetails.salary) || job.salary || 'Competitive';
  var salaryType = (fullDetails && fullDetails.salary_type) || job.salary_type || 'estimated';
  var isExact = salaryType === 'exact';
  var isLeetCode = salaryType === 'leetcode_verified';

  var matchBadge = '';
  if (match) {
    var mc = match.score >= 80
      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
      : 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300';
    matchBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-black ' + mc + '">' + match.score + '% Match</span>';
  }

  var skillsHtml = '';
  if (job.skills && Array.isArray(job.skills) && job.skills.length) {
    skillsHtml = '<div><span class="text-xs font-bold text-slate-700 dark:text-slate-300 mb-2 block">Technologies &amp; Skills</span><div class="flex flex-wrap gap-1.5">';
    for (var si = 0; si < job.skills.length; si++) {
      var s = job.skills[si];
      var isMatch = state.resumeProfile && (state.resumeProfile.skills || []).some(function(cs) { return cs.toLowerCase() === s.toLowerCase(); });
      var sc = isMatch
        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
        : 'bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300 border border-brand-500/20';
      skillsHtml += '<span class="px-2.5 py-1 rounded-lg text-xs font-semibold ' + sc + '">' + (isMatch ? '&#10003; ' : '') + escapeHtml(s) + '</span>';
    }
    skillsHtml += '</div></div>';
  }

  var bmIcon = isSaved ? 'text-amber-500 fill-amber-500' : '';

  var salaryBoxClass = isExact 
    ? 'bg-emerald-50/70 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800'
    : isLeetCode 
    ? 'bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800'
    : 'bg-slate-50 dark:bg-slate-800/60 border-slate-100 dark:border-slate-800';

  var salaryLabel = isExact ? 'Verified Pay' : isLeetCode ? 'LeetCode Verified' : 'Indian Market Est.';
  var salaryLabelClass = isExact ? 'text-emerald-700 dark:text-emerald-300' : isLeetCode ? 'text-indigo-700 dark:text-indigo-300' : 'text-slate-400';
  var salaryValClass = isExact ? 'text-emerald-800 dark:text-emerald-200' : isLeetCode ? 'text-indigo-800 dark:text-indigo-200' : 'text-amber-600 dark:text-amber-400';

  var h = '<div class="flex flex-col h-full space-y-5">'
    + '<div class="flex items-start justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">'
    + '<div class="flex items-center space-x-4">'
    + '<div class="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center overflow-hidden shrink-0 shadow-sm">'
    + '<img src="' + escapeHtml(logo) + '" alt="' + escapeHtml(job.company_name) + '" class="w-full h-full object-cover" onerror="this.onerror=null;this.src=\'' + fallback + '\';" />'
    + '</div>'
    + '<div>'
    + '<div class="flex items-center space-x-2 flex-wrap">'
    + '<h2 class="text-xl font-bold text-slate-900 dark:text-white leading-snug">' + escapeHtml(job.title) + '</h2>'
    + matchBadge
    + '</div>'
    + '<div class="flex items-center space-x-2 text-xs text-slate-600 dark:text-slate-400 mt-1">'
    + '<span class="font-semibold text-brand-600 dark:text-brand-400">' + escapeHtml(job.company_name) + '</span>'
    + '<span>&middot;</span><span>' + escapeHtml(job.location) + '</span>'
    + '<span>&middot;</span><span>' + escapeHtml(job.posted_time) + '</span>'
    + '</div></div></div>'
    + '<button data-detail-bookmark-id="' + escapeHtml(job.id) + '" class="p-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-amber-500 transition shrink-0">'
    + '<i data-lucide="bookmark" class="w-5 h-5 ' + bmIcon + '"></i></button>'
    + '</div>'

    // ACTION BUTTONS: Auto-Apply with AI + Direct LinkedIn Apply + Cover Letter
    + '<div class="flex flex-wrap gap-2.5 items-center">'
    + '<button id="startAutoApplyBtn" class="flex-1 inline-flex items-center justify-center px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-brand-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white font-bold text-xs sm:text-sm shadow-md shadow-indigo-500/20 transition space-x-2">'
    + '<i data-lucide="bot" class="w-4 h-4"></i><span>⚡ Auto-Apply with AI</span></button>'
    + '<a href="' + escapeHtml(applyUrl) + '" target="_blank" rel="noopener noreferrer" class="px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold text-xs sm:text-sm transition flex items-center space-x-1.5">'
    + '<span>Manual</span><i data-lucide="external-link" class="w-3.5 h-3.5"></i></a>'
    + '<button id="genCoverLetterBtn" class="px-3.5 py-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs sm:text-sm font-semibold transition inline-flex items-center space-x-1.5">'
    + '<i data-lucide="sparkles" class="w-4 h-4 text-indigo-500"></i><span>Cover Letter</span></button>'
    + '</div>'

    + '<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 py-2">'
    + '<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800"><span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Workplace</span><span class="font-bold text-xs sm:text-sm text-slate-900 dark:text-white mt-0.5 block">' + escapeHtml(job.workplace_type) + '</span></div>'
    + '<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800"><span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Job Type</span><span class="font-bold text-xs sm:text-sm text-slate-900 dark:text-white mt-0.5 block">' + escapeHtml(job.job_type) + '</span></div>'
    + '<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800"><span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Required Exp</span><span class="font-bold text-xs sm:text-sm text-indigo-600 dark:text-indigo-400 mt-0.5 block truncate">🎯 ' + escapeHtml(job.experience_required || (details && details.experience_required) || '2–4 Years') + '</span></div>'
    + '<div class="p-3 rounded-xl ' + salaryBoxClass + ' border">'
    + '<span class="text-[11px] font-semibold ' + salaryLabelClass + ' uppercase tracking-wider block">' + salaryLabel + '</span>'
    + '<span class="font-bold text-xs sm:text-sm ' + salaryValClass + ' mt-0.5 block truncate">' + escapeHtml(salaryDisplay) + '</span>'
    + '</div>'
    + '</div>'
    + skillsHtml
    + '<div class="pt-2 flex-1">'
    + '<h4 class="font-bold text-sm text-slate-900 dark:text-white mb-2.5">Job Description</h4>'
    + '<div class="prose dark:prose-invert max-w-none text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed overflow-y-auto max-h-[360px] pr-2">'
    + desc + '</div></div></div>';

  jobDetailsPane.innerHTML = h;

  var dbBtn = jobDetailsPane.querySelector('[data-detail-bookmark-id]');
  if (dbBtn) dbBtn.addEventListener('click', function() { toggleBookmark(job.id); });

  // Auto-Apply Button Click Handler
  var aaBtn = document.getElementById('startAutoApplyBtn');
  if (aaBtn) {
    aaBtn.addEventListener('click', function() {
      triggerAutoApply(job);
    });
  }

  var glBtn = document.getElementById('genCoverLetterBtn');
  if (glBtn) {
    glBtn.addEventListener('click', function() {
      if (!state.resumeProfile) {
        alert('Upload your resume first!');
        if (openResumeBtn) openResumeBtn.click();
        return;
      }
      glBtn.disabled = true;
      glBtn.innerText = 'Generating...';
      fetch('/api/resume/cover-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_profile: state.resumeProfile, job: job })
      })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        coverLetterText.value = d.cover_letter;
        coverLetterModal.classList.remove('hidden');
        coverLetterModal.classList.add('flex');
      })
      .catch(function() { alert('Cover letter generation failed'); })
      .finally(function() {
        glBtn.disabled = false;
        glBtn.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4 text-indigo-500"></i><span>Cover Letter</span>';
        safeCreateIcons();
      });
    });
  }

  safeCreateIcons();
}

// ----------------- Auto-Apply Engine UI Logic ----------------- //

function triggerAutoApply(job) {
  if (!autoApplyModal) return;

  autoApplyJobTitle.innerText = job.title;
  autoApplyCompany.innerText = (job.company_name || 'Target Employer') + ' \u00b7 Playwright Agent Active';
  autoApplyStatusBadge.innerText = 'INITIALIZING';
  autoApplyStatusBadge.className = 'px-2.5 py-0.5 text-[11px] font-black rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300';
  autoApplyLogs.innerHTML = '<p>[00:00] Initializing Playwright Chromium Browser Agent...</p>';
  autoApplyQuestionCard.classList.add('hidden');

  autoApplyModal.classList.remove('hidden');
  autoApplyModal.classList.add('flex');
  safeCreateIcons();

  var candidateSkills = state.resumeProfile ? (state.resumeProfile.skills || []) : ['Python', 'FastAPI', 'React', 'SQL'];
  var expYears = state.resumeProfile ? (state.resumeProfile.experience_years || 4) : 4;
  var applyUrl = job.linkedin_url || ('https://www.linkedin.com/jobs/view/' + job.id);

  var directLink = document.getElementById('autoApplyDirectLink');
  if (directLink) directLink.href = applyUrl;

  // Open the application page directly in a new tab in your active browser
  try {
    window.open(applyUrl, '_blank');
  } catch(e) {}

  fetch('/api/apply/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_id: String(job.id),
      job_title: job.title,
      company_name: job.company_name,
      apply_url: applyUrl,
      candidate_skills: candidateSkills,
      experience_years: expYears
    })
  })
  .then(function(r) { return r.json(); })
  .then(function(res) {
    state.activeApplySessionId = res.session_id;
    if (state.applyPollingTimer) clearInterval(state.applyPollingTimer);
    state.applyPollingTimer = setInterval(pollApplySessionStatus, 1200);
  })
  .catch(function(err) {
    autoApplyLogs.innerHTML += '<p class="text-rose-400">[Error] Failed to launch Playwright task: ' + escapeHtml(err.message) + '</p>';
  });
}

function pollApplySessionStatus() {
  if (!state.activeApplySessionId) return;

  fetch('/api/apply/session/' + state.activeApplySessionId)
    .then(function(r) { return r.json(); })
    .then(function(session) {
      autoApplyStatusBadge.innerText = session.status;
      
      // Update Stepper
      updateStepperUI(session.status);

      // Render Logs
      if (session.logs && session.logs.length) {
        autoApplyLogs.innerHTML = session.logs.map(function(l) {
          var colorClass = l.indexOf('Prompting') >= 0 ? 'text-amber-300 font-bold' : l.indexOf('🎉') >= 0 ? 'text-emerald-300 font-bold' : 'text-emerald-400';
          return '<p class="' + colorClass + '">' + escapeHtml(l) + '</p>';
        }).join('');
        autoApplyLogs.scrollTop = autoApplyLogs.scrollHeight;
      }

      // Check if recruiter asked a question that needs user input!
      if (session.status === 'WAITING_FOR_USER_INPUT' && session.pending_question) {
        autoApplyStatusBadge.className = 'px-2.5 py-0.5 text-[11px] font-black rounded-full bg-amber-100 text-amber-900 border border-amber-300 animate-pulse';
        promptQuestionText.innerText = session.pending_question.question;
        promptAnswerInput.value = session.pending_question.suggested_answer || '';
        autoApplyQuestionCard.classList.remove('hidden');
        promptAnswerInput.focus();
      } else {
        autoApplyQuestionCard.classList.add('hidden');
      }

      if (session.status === 'REVIEW_READY' || session.status === 'SUBMITTED') {
        autoApplyStatusBadge.className = 'px-2.5 py-0.5 text-[11px] font-black rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300';
        if (state.applyPollingTimer) clearInterval(state.applyPollingTimer);
      } else if (session.status === 'ERROR') {
        autoApplyStatusBadge.className = 'px-2.5 py-0.5 text-[11px] font-black rounded-full bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300';
        if (state.applyPollingTimer) clearInterval(state.applyPollingTimer);
      }
    })
    .catch(function(e) {
      console.error('Session poll error', e);
    });
}

function updateStepperUI(status) {
  var s1 = document.getElementById('step1');
  var s2 = document.getElementById('step2');
  var s3 = document.getElementById('step3');
  var s4 = document.getElementById('step4');
  if (!s1 || !s2 || !s3 || !s4) return;

  var activeClass = 'p-2 rounded-xl bg-indigo-500 text-white font-bold shadow-sm';
  var doneClass = 'p-2 rounded-xl bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold';
  var idleClass = 'p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700';

  if (status === 'CONNECTING' || status === 'INITIALIZING') {
    s1.className = activeClass; s2.className = idleClass; s3.className = idleClass; s4.className = idleClass;
  } else if (status === 'OPENING_PORTAL') {
    s1.className = doneClass; s2.className = activeClass; s3.className = idleClass; s4.className = idleClass;
  } else if (status === 'FILLING_FORM' || status === 'WAITING_FOR_USER_INPUT') {
    s1.className = doneClass; s2.className = doneClass; s3.className = activeClass; s4.className = idleClass;
  } else if (status === 'REVIEW_READY' || status === 'SUBMITTED') {
    s1.className = doneClass; s2.className = doneClass; s3.className = doneClass; s4.className = doneClass;
  }
}

function submitUserPromptAnswer() {
  if (!state.activeApplySessionId) return;
  var ans = promptAnswerInput.value.trim();
  if (!ans) { alert('Please enter your answer.'); return; }

  submitPromptAnswerBtn.disabled = true;
  submitPromptAnswerBtn.innerText = 'Submitting...';

  fetch('/api/apply/session/' + state.activeApplySessionId + '/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answer: ans })
  })
  .then(function(r) { return r.json(); })
  .then(function() {
    autoApplyQuestionCard.classList.add('hidden');
    showToast('Answer submitted & saved to profile memory!');
  })
  .catch(function(e) {
    alert('Answer submission failed: ' + e.message);
  })
  .finally(function() {
    submitPromptAnswerBtn.disabled = false;
    submitPromptAnswerBtn.innerHTML = '<span>Submit &amp; Continue Application</span><i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>';
    safeCreateIcons();
  });
}

function loadAndOpenAutoApplySettings() {
  fetch('/api/apply/profile')
    .then(function(r) { return r.json(); })
    .then(function(prof) {
      if (profFullName) profFullName.value = prof.full_name || '';
      if (profEmail) profEmail.value = prof.email || '';
      if (profPhone) profPhone.value = prof.phone || '';
      if (profCity) profCity.value = prof.city || '';
      if (profNotice) profNotice.value = prof.notice_period || '30 days';
      if (profCurrentCtc) profCurrentCtc.value = prof.current_ctc || '18 LPA';
      if (profExpectedCtc) profExpectedCtc.value = prof.expected_ctc || '30 LPA';
      if (profLinkedin) profLinkedin.value = prof.linkedin_url || '';
      if (profGithub) profGithub.value = prof.github_url || '';
      if (profAuth) profAuth.value = prof.work_authorization || 'Yes';

      if (autoApplySettingsModal) {
        autoApplySettingsModal.classList.remove('hidden');
        autoApplySettingsModal.classList.add('flex');
      }
      safeCreateIcons();
    });
}

function handleSaveAutoApplyProfile(e) {
  e.preventDefault();
  var payload = {
    full_name: profFullName ? profFullName.value.trim() : '',
    email: profEmail ? profEmail.value.trim() : '',
    phone: profPhone ? profPhone.value.trim() : '',
    city: profCity ? profCity.value.trim() : '',
    notice_period: profNotice ? profNotice.value : '30 days',
    current_ctc: profCurrentCtc ? profCurrentCtc.value.trim() : '18 LPA',
    expected_ctc: profExpectedCtc ? profExpectedCtc.value.trim() : '30 LPA',
    linkedin_url: profLinkedin ? profLinkedin.value.trim() : '',
    github_url: profGithub ? profGithub.value.trim() : '',
    work_authorization: profAuth ? profAuth.value : 'Yes'
  };

  fetch('/api/apply/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(function(r) { return r.json(); })
  .then(function() {
    autoApplySettingsModal.classList.add('hidden');
    autoApplySettingsModal.classList.remove('flex');
    showToast('Auto-Apply profile & screening preferences saved!');
  })
  .catch(function(err) {
    alert('Save failed: ' + err.message);
  });
}

function toggleBookmark(jobId) {
  var idx = state.bookmarks.findIndex(function(b) { return String(b.id) === String(jobId); });
  if (idx >= 0) {
    state.bookmarks.splice(idx, 1);
    showToast('Removed from saved');
  } else {
    var job = state.jobs.find(function(j) { return String(j.id) === String(jobId); }) || state.selectedJob;
    if (job) { state.bookmarks.push(job); showToast('Saved!'); }
  }
  localStorage.setItem('saved_jobs', JSON.stringify(state.bookmarks));
  updateBookmarkUI();
  renderJobsList();
  if (state.selectedJob && String(state.selectedJob.id) === String(jobId)) selectJob(jobId);
}

function updateBookmarkUI() {
  var c = state.bookmarks.length;
  if (bookmarkCount) bookmarkCount.innerText = c;
  if (modalBookmarkCount) modalBookmarkCount.innerText = c;
}

function renderBookmarksModal() {
  if (!bookmarksList) return;
  if (!state.bookmarks.length) {
    bookmarksList.innerHTML = '<div class="text-center py-12 text-slate-400"><p class="font-semibold text-sm">No saved jobs yet</p></div>';
    return;
  }
  var h = '';
  for (var i = 0; i < state.bookmarks.length; i++) {
    var job = state.bookmarks[i];
    var fb = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(job.company_name || 'J') + '&background=0a66c2&color=fff&size=40';
    var lg = job.company_logo || fb;
    h += '<div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between gap-3">'
      + '<div class="flex items-center space-x-3 min-w-0">'
      + '<img src="' + escapeHtml(lg) + '" alt="' + escapeHtml(job.company_name) + '" class="w-10 h-10 rounded-lg object-cover bg-slate-100 dark:bg-slate-800 shrink-0" />'
      + '<div class="min-w-0"><h4 class="font-bold text-sm text-slate-900 dark:text-white truncate">' + escapeHtml(job.title) + '</h4>'
      + '<p class="text-xs text-slate-500 truncate">' + escapeHtml(job.company_name) + '</p></div></div>'
      + '<a href="' + escapeHtml(job.linkedin_url) + '" target="_blank" class="px-3 py-1.5 bg-brand-500 text-white rounded-lg text-xs font-semibold hover:bg-brand-600 transition">Apply</a>'
      + '</div>';
  }
  bookmarksList.innerHTML = h;
}

function fetchAndShowStats() {
  fetch('/api/stats')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var sc = document.getElementById('skillsTrendCloud');
      if (sc && data.popular_skills) {
        sc.innerHTML = data.popular_skills.map(function(s) {
          return '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">' + escapeHtml(s) + '</span>';
        }).join('');
      }
      var cg = document.getElementById('companiesTrendGrid');
      if (cg && data.top_companies) {
        cg.innerHTML = data.top_companies.map(function(c) {
          return '<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200/60 dark:border-slate-700 text-center"><span class="font-bold text-xs text-slate-800 dark:text-slate-200 block">' + escapeHtml(c) + '</span></div>';
        }).join('');
      }
      if (statsModal) { statsModal.classList.remove('hidden'); statsModal.classList.add('flex'); }
      safeCreateIcons();
    })
    .catch(function() { showToast('Stats load failed'); });
}

var toastTimer;
function showToast(message) {
  var toast = document.getElementById('toast');
  var toastMsg = document.getElementById('toastMsg');
  if (!toast || !toastMsg) return;
  toastMsg.innerText = message;
  toast.classList.remove('opacity-0', 'translate-y-20');
  toast.classList.add('opacity-100', 'translate-y-0');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function() {
    toast.classList.remove('opacity-100', 'translate-y-0');
    toast.classList.add('opacity-0', 'translate-y-20');
  }, 2800);
}

function switchView(viewName) {
  state.currentView = viewName;
  if (viewName === 'posts') {
    if (jobsMainSection) jobsMainSection.classList.add('hidden');
    if (postsViewSection) postsViewSection.classList.remove('hidden');
    if (viewPostsTabBtn) {
      viewPostsTabBtn.className = 'px-4 py-2 rounded-xl text-xs sm:text-sm font-bold bg-indigo-600 text-white shadow-md shadow-indigo-600/20 flex items-center space-x-2 transition';
    }
    if (viewJobsTabBtn) {
      viewJobsTabBtn.className = 'px-4 py-2 rounded-xl text-xs sm:text-sm font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-brand-500 hover:text-brand-500 flex items-center space-x-2 transition';
    }
    fetchPosts();
  } else {
    if (postsViewSection) postsViewSection.classList.add('hidden');
    if (jobsMainSection) jobsMainSection.classList.remove('hidden');
    if (viewJobsTabBtn) {
      viewJobsTabBtn.className = 'px-4 py-2 rounded-xl text-xs sm:text-sm font-bold bg-brand-500 text-white shadow-md shadow-brand-500/20 flex items-center space-x-2 transition';
    }
    if (viewPostsTabBtn) {
      viewPostsTabBtn.className = 'px-4 py-2 rounded-xl text-xs sm:text-sm font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-indigo-500 hover:text-indigo-500 flex items-center space-x-2 transition';
    }
    fetchJobs();
  }
  safeCreateIcons();
}

function fetchPosts() {
  if (postsCardsContainer) {
    postsCardsContainer.innerHTML = '<div class="col-span-full py-16 text-center text-slate-400 space-y-3"><div class="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div><p class="text-xs font-semibold">Scanning LinkedIn hiring feed & extracting recruiter contacts...</p></div>';
  }
  if (postsCountBadge) postsCountBadge.innerText = 'Scanning feed...';

  var p = new URLSearchParams({
    keywords: state.keywords || 'Software Engineer',
    location: state.location || 'India',
    top_tier_only: state.top_tier_only
  });

  fetch('/api/posts/search?' + p.toString())
    .then(function(res) { return res.json(); })
    .then(function(data) {
      state.posts = data.posts || [];
      if (postsCountBadge) postsCountBadge.innerText = state.posts.length + ' Live Hiring Posts Found';
      renderPostsList();
    })
    .catch(function(err) {
      console.error('Posts fetch error', err);
      if (postsCardsContainer) {
        postsCardsContainer.innerHTML = '<div class="col-span-full py-12 text-center text-rose-500 text-xs">Failed to load hiring posts.</div>';
      }
    });
}

function renderPostsList() {
  if (!postsCardsContainer) return;
  if (!state.posts.length) {
    postsCardsContainer.innerHTML = '<div class="col-span-full py-16 text-center text-slate-500"><p class="font-bold text-sm">No recruiter hiring posts found matching your keywords.</p></div>';
    return;
  }

  var html = '';
  for (var i = 0; i < state.posts.length; i++) {
    var p = state.posts[i];
    var authorName = escapeHtml(p.author_name || 'Hiring Manager');
    var authorTitle = escapeHtml(p.author_title || 'Engineering Leader');
    var authorAvatar = p.author_avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(authorName);
    var content = escapeHtml(p.content || '');
    var postedTime = escapeHtml(p.posted_time || 'Recent');
    var expBadge = p.experience_required ? '<span class="px-2 py-0.5 rounded-md font-semibold bg-indigo-50 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">🎯 ' + escapeHtml(p.experience_required) + '</span>' : '';
    var salaryBadge = p.salary_snippet ? '<span class="px-2 py-0.5 rounded-md font-bold bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">💰 ' + escapeHtml(p.salary_snippet) + '</span>' : '';
    var tierBadge = p.is_top_tier ? '<span class="px-2 py-0.5 rounded-md font-black bg-amber-50 text-amber-900 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800">⭐ 30+ LPA</span>' : '';

    var primaryEmail = (p.extracted_emails && p.extracted_emails.length) ? p.extracted_emails[0] : '';
    var emailActionBadge = primaryEmail
      ? '<button onclick="copyDirectEmail(\'' + escapeHtml(primaryEmail) + '\')" class="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 dark:bg-indigo-950/80 dark:hover:bg-indigo-900 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 flex items-center gap-1.5 transition" title="Click to copy recruiter email"><i data-lucide="mail" class="w-3.5 h-3.5 text-indigo-500"></i> <span>' + escapeHtml(primaryEmail) + '</span> <i data-lucide="copy" class="w-3 h-3 text-slate-400"></i></button>'
      : '<span class="text-xs text-slate-400">DM on LinkedIn</span>';

    var skillsHtml = '';
    if (p.skills && p.skills.length) {
      skillsHtml = '<div class="flex flex-wrap gap-1 mt-2">' + p.skills.map(function(s) {
        return '<span class="px-2 py-0.5 text-[10px] font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">' + escapeHtml(s) + '</span>';
      }).join('') + '</div>';
    }

    html += '<div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between hover:border-indigo-400 dark:hover:border-indigo-600 transition space-y-4">'
      + '<div>'
      + '<div class="flex items-start justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">'
      + '<div class="flex items-center space-x-3">'
      + '<img src="' + escapeHtml(authorAvatar) + '" class="w-11 h-11 rounded-full object-cover border border-slate-200 dark:border-slate-700 shrink-0" alt="' + authorName + '" />'
      + '<div class="min-w-0">'
      + '<h4 class="font-bold text-sm text-slate-900 dark:text-white truncate">' + authorName + '</h4>'
      + '<p class="text-xs text-slate-500 truncate">' + authorTitle + '</p>'
      + '</div>'
      + '</div>'
      + '<span class="text-[11px] text-slate-400 shrink-0">' + postedTime + '</span>'
      + '</div>'
      + '<div class="mt-3 flex flex-wrap items-center gap-1.5 text-[11px]">'
      + tierBadge
      + expBadge
      + salaryBadge
      + '</div>'
      + '<div class="mt-3 text-xs sm:text-sm text-slate-700 dark:text-slate-300 whitespace-pre-line leading-relaxed font-normal line-clamp-6 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-100 dark:border-slate-800">'
      + content
      + '</div>'
      + skillsHtml
      + '</div>'
      + '<div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">'
      + emailActionBadge
      + '<div class="flex items-center space-x-2 justify-end">'
      + '<button onclick="openColdEmailForPostIndex(' + i + ')" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-gradient-to-r from-indigo-500 to-brand-500 hover:from-indigo-600 hover:to-brand-600 text-white shadow-sm flex items-center space-x-1.5 transition">'
      + '<i data-lucide="sparkles" class="w-3.5 h-3.5"></i>'
      + '<span>AI Cold Email</span>'
      + '</button>'
      + '<a href="' + escapeHtml(p.post_url) + '" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 flex items-center space-x-1 transition">'
      + '<span>Open Post</span>'
      + '<i data-lucide="external-link" class="w-3.5 h-3.5 ml-1"></i>'
      + '</a>'
      + '</div>'
      + '</div>'
      + '</div>';
  }

  postsCardsContainer.innerHTML = html;
  safeCreateIcons();
}

function copyDirectEmail(emailStr) {
  navigator.clipboard.writeText(emailStr)
    .then(function() { showToast('✅ Copied recruiter email: ' + emailStr); })
    .catch(function() { showToast('Copied'); });
}

function openColdEmailForPostIndex(postIdx) {
  var post = state.posts[postIdx];
  if (!post) return;

  if (coldEmailRecipient) coldEmailRecipient.value = (post.extracted_emails && post.extracted_emails.length) ? post.extracted_emails[0] : 'hiring@company.com';
  if (coldEmailTitle) coldEmailTitle.innerText = 'Cold Outreach: ' + (post.author_company || 'Engineering Team');
  if (coldEmailSubtitle) coldEmailSubtitle.innerText = 'To ' + (post.author_name || 'Hiring Manager') + ' (' + (post.author_title || '') + ')';
  
  if (coldEmailSubject) coldEmailSubject.value = 'Generating email...';
  if (coldEmailBody) coldEmailBody.value = 'Drafting personalized outreach email based on post and your resume...';

  if (coldEmailModal) {
    coldEmailModal.classList.remove('hidden');
    coldEmailModal.classList.add('flex');
    safeCreateIcons();
  }

  fetch('/api/posts/cold-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      post: post,
      resume_profile: state.resumeProfile
    })
  })
  .then(function(res) { return res.json(); })
  .then(function(data) {
    if (coldEmailSubject) coldEmailSubject.value = data.subject || 'Application: Software Engineer';
    if (coldEmailBody) coldEmailBody.value = data.body || '';
  })
  .catch(function(err) {
    console.error('Cold email error', err);
    if (coldEmailBody) coldEmailBody.value = 'Failed to generate cold email.';
  });
}


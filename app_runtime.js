const toast = document.getElementById("toast");
const placeholderButtons = document.querySelectorAll("[data-placeholder]");
const playOpenButton = document.getElementById("playOpenButton");
const playScreen = document.getElementById("playScreen");
const playBackButton = document.getElementById("playBack");
const onlineModeButton = document.getElementById("onlineModeButton");
const onlineScreen = document.getElementById("onlineScreen");
const onlineListView = document.getElementById("onlineListView");
const onlineRoomView = document.getElementById("onlineRoomView");
const onlineLobbyList = document.getElementById("onlineLobbyList");
const createLobbyButton = document.getElementById("createLobbyButton");
const onlineBackButton = document.getElementById("onlineBack");
const onlinePlayerGrid = document.getElementById("onlinePlayerGrid");
const onlineRoomCount = document.getElementById("onlineRoomCount");
const onlineObserverCard = document.getElementById("onlineObserverCard");
const onlineRoomBanner = document.getElementById("onlineRoomBanner");
const gameScreen = document.getElementById("gameScreen");
const gameMusicToggle = document.getElementById("gameMusicToggle");
const gameSurrenderButton = document.getElementById("gameSurrenderButton");
const gameTurnRibbon = document.getElementById("gameTurnRibbon");
const gameTurnTrack = document.getElementById("gameTurnTrack");
const gameDayOverlay = document.getElementById("gameDayOverlay");
const gameDayText = document.getElementById("gameDayText");
const gameFinalScreen = document.getElementById("gameFinalScreen");
const gameFinalWinner = document.getElementById("gameFinalWinner");
const gameFinalList = document.getElementById("gameFinalList");
const gameFinalCloseButton = document.getElementById("gameFinalCloseButton");
const gameWaitingScreen = document.getElementById("gameWaitingScreen");
const gameWaitingTitle = document.getElementById("gameWaitingTitle");
const gameWaitingSubtitle = document.getElementById("gameWaitingSubtitle");
const spectatorCameraOverlay = document.getElementById("spectatorCameraOverlay");
const spectatorCameraName = document.getElementById("spectatorCameraName");
const gameActionLog = document.getElementById("gameActionLog");
const gameSelectScreen = document.getElementById("gameSelectScreen");
const gameSelectRow = document.getElementById("gameSelectRow");
const gameSelectDescription = document.getElementById("gameSelectDescription");
const gameRoomScreen = document.getElementById("gameRoomScreen");
const gameRoomBack = document.getElementById("gameRoomBack");
const statUpgradeOverlay = document.getElementById("statUpgradeOverlay");
const statUpgradeReward = document.getElementById("statUpgradeReward");
const statUpgradePoints = document.getElementById("statUpgradePoints");
const statUpgradeList = document.getElementById("statUpgradeList");
const statUpgradeCloseButton = document.getElementById("statUpgradeCloseButton");
const eventOverlay = document.getElementById("eventOverlay");
const eventIcon = document.getElementById("eventIcon");
const eventIntro = document.getElementById("eventIntro");
const eventRollerWrap = document.getElementById("eventRollerWrap");
const eventRoller = document.getElementById("eventRoller");
const eventEffect = document.getElementById("eventEffect");
const eventChoices = document.getElementById("eventChoices");
const eventConfirmButton = document.getElementById("eventConfirmButton");
const inventoryOverlay = document.getElementById("inventoryOverlay");
const inventoryTitle = document.getElementById("inventoryTitle");
const inventoryList = document.getElementById("inventoryList");
const inventoryPreviewName = document.getElementById("inventoryPreviewName");
const inventoryPreviewEffect = document.getElementById("inventoryPreviewEffect");
const inventoryUseButton = document.getElementById("inventoryUseButton");
const inventoryCloseButton = document.getElementById("inventoryCloseButton");
const vnOverlay = document.getElementById("vnOverlay");
const vnWindow = document.querySelector(".vn-window");
const vnBg = document.querySelector(".vn-window-bg");
const vnObjectPrompt = document.getElementById("vnObjectPrompt");
const vnHotspots = document.getElementById("vnHotspots");
const vnPopup = document.getElementById("vnPopup");
const vnPopupText = document.getElementById("vnPopupText");
const vnPopupActions = document.getElementById("vnPopupActions");
const vnNameplate = document.getElementById("vnNameplate");
const vnSpeaker = document.getElementById("vnSpeaker");
const vnPortrait = document.getElementById("vnPortrait");
const vnText = document.getElementById("vnText");
const vnChoices = document.getElementById("vnChoices");
const vnCloseButton = document.getElementById("vnCloseButton");
const tennaOverlay = document.getElementById("tennaOverlay");
const tennaPodiums = document.getElementById("tennaPodiums");
const tennaHost = document.getElementById("tennaHost");
const tennaSpeech = document.getElementById("tennaSpeech");
const tennaNext = document.getElementById("tennaNext");
const tennaCollapse = document.getElementById("tennaCollapse");
const tennaBoard = document.getElementById("tennaBoard");
const tennaQuestion = document.getElementById("tennaQuestion");
const tennaMini = document.getElementById("tennaMini");
const tennaMiniText = document.getElementById("tennaMiniText");
const gameDetailsScreen = document.getElementById("gameDetailsScreen");
const detailsEventOverlay = document.getElementById("detailsEventOverlay");
const detailsEventIcon = document.getElementById("detailsEventIcon");
const detailsEventIntro = document.getElementById("detailsEventIntro");
const detailsEventEffect = document.getElementById("detailsEventEffect");
const detailsEventChoices = document.getElementById("detailsEventChoices");
const detailsEventConfirmButton = document.getElementById("detailsEventConfirmButton");
const trainTicketButton = document.getElementById("trainTicketButton");
const violinStealButton = document.getElementById("violinStealButton");
const trainDamageFlash = document.getElementById("trainDamageFlash");
const gameDetailsLightbox = document.getElementById("gameDetailsLightbox");
const gameDetailsLightboxImage = document.getElementById("gameDetailsLightboxImage");
const gameDetailsLightboxClose = document.getElementById("gameDetailsLightboxClose");
const gameDetailsProgress = document.getElementById("gameDetailsProgress");
const gameDetailsProgressValue = document.getElementById("gameDetailsProgressValue");
const gameDetailsProgressNote = document.getElementById("gameDetailsProgressNote");
const gameDetailsBaseMedia = document.getElementById("gameDetailsBaseMedia");
const gameDetailsBaseName = document.getElementById("gameDetailsBaseName");
const gameDetailsBaseCode = document.getElementById("gameDetailsBaseCode");
const gameDetailsBaseRisk = document.getElementById("gameDetailsBaseRisk");
const gameDetailsDmgType = document.getElementById("gameDetailsDmgType");
const gameDetailsDmgAmount = document.getElementById("gameDetailsDmgAmount");
const gameDetailsGoodRange = document.getElementById("gameDetailsGoodRange");
const gameDetailsBadRange = document.getElementById("gameDetailsBadRange");
const gameDetailsHiddenHintSlot = document.getElementById("gameDetailsHiddenHintSlot");
const gameDetailsHintsList = document.getElementById("gameDetailsHintsList");
const gameDetailsDescriptionSlot = document.getElementById("gameDetailsDescriptionSlot");
const gameDetailsKlipotaValue = document.getElementById("gameDetailsKlipotaValue");
const gameDetailsEscapeText = document.getElementById("gameDetailsEscapeText");
const gameDetailsRpValue = document.getElementById("gameDetailsRpValue");
const gameDetailsCloseButton = document.getElementById("gameDetailsCloseButton");
const gameRoomKlipotaBadge = document.getElementById("gameRoomKlipotaBadge");
const gameRoomKlipotaMark = document.getElementById("gameRoomKlipotaMark");
const gameRoomRpValue = document.getElementById("gameRoomRpValue");
const gameRoomName = document.getElementById("gameRoomName");
const gameRoomPenalty = document.getElementById("gameRoomPenalty");
const gameRoomModel = document.getElementById("gameRoomModel");
const gameRoomAgent = document.getElementById("gameRoomAgent");
const gameRoomInitialEffect = document.getElementById("gameRoomInitialEffect");
const gameDamageFlash = document.getElementById("gameDamageFlash");
const gameRoomResultScore = document.getElementById("gameRoomResultScore");
const gameRoomResultGrid = document.getElementById("gameRoomResultGrid");
const gameRoomNoRisk = document.getElementById("gameRoomNoRisk");
const gameRoomWorkMeta = document.getElementById("gameRoomWorkMeta");
const gameRoomDebug = document.getElementById("gameRoomDebug");
const gameRoomAdminPanel = document.getElementById("gameRoomAdminPanel");
const gameRoomPlayerStatus = document.getElementById("gameRoomPlayerStatus");
const gameRoomGlobals = document.getElementById("gameRoomGlobals");
const gameRoomAdminStats = document.getElementById("gameRoomAdminStats");
const adminAddStatsButton = document.getElementById("adminAddStatsButton");
const adminAddRpButton = document.getElementById("adminAddRpButton");
const adminRollPsychosisButton = document.getElementById("adminRollPsychosisButton");
const adminTrainTenSecondsButton = document.getElementById("adminTrainTenSecondsButton");
const adminX125Button = document.getElementById("adminX125Button");
const adminDayInput = document.getElementById("adminDayInput");
const adminSetDayButton = document.getElementById("adminSetDayButton");
const adminAnomalyInput = document.getElementById("adminAnomalyInput");
const adminSpawnAnomalyButton = document.getElementById("adminSpawnAnomalyButton");
const adminNextAnomalyInput = document.getElementById("adminNextAnomalyInput");
const adminD20RollInput = document.getElementById("adminD20RollInput");
const adminForceD20RollButton = document.getElementById("adminForceD20RollButton");
const adminAlastorTaskInput = document.getElementById("adminAlastorTaskInput");
const adminForceAlastorTaskButton = document.getElementById("adminForceAlastorTaskButton");
const adminForceNextAnomalyButton = document.getElementById("adminForceNextAnomalyButton");
const gameRoomActionMenu = document.getElementById("gameRoomActionMenu");
const gameRoomWorkMenu = document.getElementById("gameRoomWorkMenu");
const gameRoomRiskMenu = document.getElementById("gameRoomRiskMenu");
const gameRoomTypeMenu = document.getElementById("gameRoomTypeMenu");
const gameRoomResultMenu = document.getElementById("gameRoomResultMenu");
const actionWorkButton = document.getElementById("actionWorkButton");
const actionInventoryButton = document.getElementById("actionInventoryButton");
const actionFleeButton = document.getElementById("actionFleeButton");
const actionFinishButton = document.getElementById("actionFinishButton");
const actionArtifactButton = document.getElementById("actionArtifactButton");
const actionViolinButton = document.getElementById("actionViolinButton");
const actionWorkBackButton = document.getElementById("actionWorkBackButton");
const actionRiskBackButton = document.getElementById("actionRiskBackButton");
const actionTypeBackButton = document.getElementById("actionTypeBackButton");
const actionRepeatWorkButton = document.getElementById("actionRepeatWorkButton");
const actionChangeWorkButton = document.getElementById("actionChangeWorkButton");
const actionReturnMenuButton = document.getElementById("actionReturnMenuButton");
const workButtonIntuition = document.getElementById("workButtonIntuition");
const workButtonInsight = document.getElementById("workButtonInsight");
const workButtonAffection = document.getElementById("workButtonAffection");
const workButtonSuppression = document.getElementById("workButtonSuppression");
const codexOpenButton = document.querySelector("[data-open-codex]");

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[char]));
}

function formatHintMarkup(value) {
  const escaped = escapeHtml(value ?? "");
  return escaped.replace(/\[red\]([\s\S]*?)\[\/red\]/gi, '<span class="hint-red">$1</span>');
}
const codexCloseButton = document.getElementById("codexClose");
const codexScreen = document.getElementById("codexScreen");
const codexGrid = document.getElementById("codexGrid");
const pagePrev = document.getElementById("pagePrev");
const pageNext = document.getElementById("pageNext");
const pageIndicator = document.getElementById("pageIndicator");
const codexDetails = document.getElementById("codexDetails");
const codexProgressValue = document.getElementById("codexProgressValue");
const leaderboardOpenButton = document.querySelector("[data-open-leaderboard]");
const leaderboardBackButton = document.getElementById("leaderboardBack");
const leaderboardScreen = document.getElementById("leaderboardScreen");
const leaderboardList = document.getElementById("leaderboardList");
const leaderboardPrev = document.getElementById("leaderboardPrev");
const leaderboardNext = document.getElementById("leaderboardNext");
const leaderboardIndicator = document.getElementById("leaderboardIndicator");
const profileButton = document.getElementById("profileButton");
const profileAvatar = document.getElementById("profileAvatar");
const profilePlaceholder = document.getElementById("profilePlaceholder");
const profileMenu = document.getElementById("profileMenu");
const profileUsername = document.getElementById("profileUsername");
const profileGlobalName = document.getElementById("profileGlobalName");
const profileLogout = document.getElementById("profileLogout");

const anomalyCustomButtonDefaults = new Map(
  [actionWorkButton, workButtonIntuition, workButtonInsight, workButtonAffection, workButtonSuppression]
    .filter(Boolean)
    .map((button) => [button.id, {
      html: button.innerHTML,
      ariaLabel: button.getAttribute("aria-label") || "",
      title: button.getAttribute("title") || ""
    }])
);

const ANOMALY_CUSTOM_BUTTONS = {
  11: {
    work: {
      suppression: {
        image: "/photo/work_room/11button.png",
        label: "Сброс"
      }
    }
  },
  63: {
    work: {
      intuition: {
        image: "/photo/work_room/63button.png",
        label: "сделка"
      },
      insight: {
        image: "/photo/work_room/63button.png",
        label: "сделка"
      },
      affection: {
        image: "/photo/work_room/63button.png",
        label: "сделка"
      },
      suppression: {
        image: "/photo/work_room/63button.png",
        label: "сделка"
      }
    }
  },
  68: {
    work: {
      insight: {
        image: "/photo/work_room/68button.png",
        label: "Передать предмет"
      }
    }
  },
  133: {
    work: {
      intuition: {
        image: "/photo/work_room/133button.png",
        label: "Жертва"
      }
    }
  }
};

let toastTimer = null;
let currentPage = 1;
const itemsPerPage = 25;
let totalPages = 1;
let codexItems = [];
let codexLoaded = false;
let leaderboardPage = 1;
let leaderboardTotalPages = 1;
const DEFAULT_LOCAL_PLAYER_ID = 287676136438104060;
let discordUser = null;
let discordOauthEnabled = false;
let onlineLobbyPoller = null;
let activeGameSignature = null;
let gameMusic = null;
let activeGameAnomalies = [];
let activeGameSelectionKey = "";
let gameStatePoller = null;
let gameStatePollBusy = false;
let lastAppliedTurnOwnerId = null;
let lastActiveGameStartedAt = null;
let deathModalActive = false;
let spectatorMode = false;
let spectatorCameraKey = "";
let spectatorNoiseTimer = null;
let cameraPublishRevision = Date.now() * 1000;
let spectatorVnVisible = false;
let lastPublishedCameraKey = "";
let activeRoomAnomalyId = null;
let roomResultTimer = null;
let detailsScrollPublishTimer = null;
let selectedWorkType = null;
let selectedRiskChoice = null;
let selectedTypeChoice = null;
let currentDetailsPayload = null;
let roomWorkResolving = false;
let d20RollInFlight = false;
let crimsonBiteResolving = false;
let activeRoomPayload = null;
let completionAlertPlayed = false;
let finishPreviewActive = false;
let upgradeModalBusy = false;
let lastFinishReward = { cp: 0, rt: 0 };
let eventModalResolver = null;
let systemEventModalQueue = Promise.resolve();
let softlockVoteSeenStatus = "";
function enqueueSystemEventModal(task) {
  const queued = systemEventModalQueue.then(task, task);
  systemEventModalQueue = queued.catch(() => {});
  return queued;
}

function ensureSoftlockOverlay() {
  let overlay = document.getElementById("softlockOverlay");
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.id = "softlockOverlay";
  overlay.className = "softlock-overlay hidden";
  overlay.innerHTML = `<div class="softlock-dialog"><h2></h2><p></p><div class="softlock-actions"></div></div>`;
  document.body.appendChild(overlay);
  return overlay;
}

function hideSoftlockOverlay() {
  document.getElementById("softlockOverlay")?.classList.add("hidden");
}

function showSoftlockDialog(title, text, choices) {
  const overlay = ensureSoftlockOverlay();
  overlay.querySelector("h2").textContent = title;
  overlay.querySelector("p").textContent = text;
  const actions = overlay.querySelector(".softlock-actions");
  actions.innerHTML = "";
  choices.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = choice.label;
    button.className = choice.danger ? "danger" : "";
    button.onclick = choice.onClick;
    actions.appendChild(button);
  });
  overlay.classList.remove("hidden");
}

function requestSoftlockVote() {
  showSoftlockDialog(
    "Софтлок",
    "Если произошел софтлок, попробуй перезагрузить страницу, если не помогло — жми Подтвердить",
    [
      { label: "Подтвердить", danger: true, onClick: async () => {
        try {
          const payload = await apiPost("/api/game/softlock-start", { user_id: currentUserId() });
          hideSoftlockOverlay();
          handleSoftlockVote(payload.softlock_vote);
          if (payload.softlock_vote?.status === "active") showInfoToast("Запрос отправлен другим живым игрокам.");
        } catch (error) { hideSoftlockOverlay(); showRuntimeErrorModal(error); }
      }},
      { label: "Отмена", onClick: hideSoftlockOverlay }
    ]
  );
}

function handleSoftlockVote(vote) {
  if (!vote?.id) return;
  const signature = `${vote.id}:${vote.status}`;
  if (vote.status === "advanced") {
    const reloadKey = `softlock-advanced:${vote.id}`;
    if (window.sessionStorage.getItem(reloadKey) === "reloaded") return;
    window.sessionStorage.setItem(reloadKey, "reloaded");
    softlockVoteSeenStatus = signature;
    hideSoftlockOverlay();
    window.location.reload();
    return;
  }
  if (vote.status === "rejected") {
    hideSoftlockOverlay();
    if (softlockVoteSeenStatus !== signature) showInfoToast("Запрос о софтлоке отклонён.");
    softlockVoteSeenStatus = signature;
    return;
  }
  if (vote.status !== "active" || vote.voted || vote.is_requester) return;
  if (softlockVoteSeenStatus === signature) return;
  softlockVoteSeenStatus = signature;
  showSoftlockDialog(
    "Софтлок?",
    `${vote.requester_name || "Игрок"} сообщает о софтлоке. Прервать текущие события и начать следующий день?`,
    [
      { label: "Подтвердить", danger: true, onClick: async () => {
        try {
          const payload = await apiPost("/api/game/softlock-vote", { user_id: currentUserId(), approve: true });
          hideSoftlockOverlay();
          handleSoftlockVote(payload.softlock_vote);
        } catch (error) { hideSoftlockOverlay(); showRuntimeErrorModal(error); }
      }},
      { label: "Отклонить", onClick: async () => {
        try {
          const payload = await apiPost("/api/game/softlock-vote", { user_id: currentUserId(), approve: false });
          hideSoftlockOverlay();
          handleSoftlockVote(payload.softlock_vote);
        } catch (error) { hideSoftlockOverlay(); showRuntimeErrorModal(error); }
      }}
    ]
  );
}
let vnModalResolver = null;
let vnTextGeneration = 0;
let detailsEventResolver = null;
let inventoryModalResolver = null;
let activeInventoryPayload = null;
let activeInventoryItem = null;
let inventoryUseBusy = false;
let pendingNextWorkDebug = null;
let debugModeEnabled = false;
let alastorTaskSignature = "";
let deferFinalResultsModal = false;
let activeTennaGame = null;
let tennaIntroIndex = 0;
let tennaIntroLines = [];
let tennaIntroSession = "";
let tennaPoseTimer = null;
let tennaCollapsed = false;
let tennaExpandedManually = false;
let tennaStageVisible = false;
let tennaReactionSignature = "";
let tennaTextTimer = null;
let tennaAutoAdvanceTimer = null;
let tennaTyping = false;
let tennaFullText = "";
let tennaPoseIndex = -1;
let tennaRenderedQuestionSignature = "";
let tennaDeadlineTimer = null;
let tennaFinalSession = "";
let tennaFinalRunning = false;
let tennaFinalLines = [];
let tennaFinalIndex = 0;
let contractSummaryShowing = false;
let targetNoticeShowing = false;

const PSYCHOSIS_ROLLER_NAMES = [
  "Никтофобия",
  "Биофобия",
  "Теофобия",
  "Антропофобия",
  "Технофобия",
  "Ничего",
  "Прозрение",
  "Мазохизм",
  "Паника",
  "Ярость"
];
let backgroundMusicTrack = "";
let brainrotMusicUrl = "";
let brainrotMusicDay = 0;
const BACKGROUND_MUSIC_PREF = "weblob-background-music";
let backgroundMusicEnabled = window.localStorage.getItem(BACKGROUND_MUSIC_PREF) !== "off";
let currentTrainTicketState = null;
let trainPauseRequest = Promise.resolve();
let x125BattleRuntime = null;
let x125AudioLock = false;
let x125IntroActive = false;
let x125PendingIntroEvent = null;

const soundPlayers = {
  hoverContainer: new Audio("/sound/DoorOn.wav"),
  selectContainer: new Audio("/sound/DoorClick.wav"),
  researchComplete: new Audio("/sound/017. Dun Don Alert.wav"),
  unlockUi: new Audio("/sound/014. Cool Sticky UI Button.wav"),
  workButton: new Audio("/sound/001. Button4.wav"),
  damageHit: new Audio("/sound/Armor_HeadOff.wav"),
  boneAttack: new Audio("/sound/Bone_Atk1.wav"),
  bossDead: new Audio("/sound/Boss_Dead.wav"),
  trainEnd: new Audio("/sound/Train_End.wav"),
  trainSell: new Audio("/sound/Train_Sell.wav"),
  tickOfDoom: new Audio("/sound/tickofdoom.wav"),
  overloadAlert: new Audio("/sound/OverloadAlert3.wav"),
  burningEyes: new Audio("/sound/BURNING EYES.mp3"),
  gasterIntro: new Audio("/sound/gasterintro.wav"),
  gasterFire: new Audio("/sound/gasterfire.wav"),
  pew: new Audio("/sound/pew.wav"),
  plusExplode: new Audio("/sound/plusexplode.wav"),
  battleHit: new Audio("/sound/mus_sfx_swipe.wav"),
  imageFriendLaugh: new Audio("/sound/IMAGEFRIEND laugh [Deltarune Chapter 34].mp3"),
  eramLaugh: new Audio("/sound/[DELTARUNE] Eram Laugh Sound..mp3"),
};

Object.values(soundPlayers).forEach((audio) => {
  audio.preload = "auto";
  audio.volume = 0.6;
});

const typeMap = { 1: "Природный", 2: "Темный", 3: "Конструкт", 4: "Абстракт", 5: "Гуманоид" };
const classMap = { 1: "ZAYIN", 2: "TETH", 3: "HE", 4: "WAW", 5: "ALEPH" };
const classMeta = {
  ZAYIN: { icon: "/photo/work_room/Risk_Zayin.png", cssClass: "class-zayin", strip: "rgb(4, 217, 43)" },
  TETH: { icon: "/photo/work_room/Risk_Teth.png", cssClass: "class-teth", strip: "rgb(0, 8, 255)" },
  HE: { icon: "/photo/work_room/Risk_He.png", cssClass: "class-he", strip: "rgb(247, 235, 5)" },
  WAW: { icon: "/photo/work_room/Risk_Waw.png", cssClass: "class-waw", strip: "rgb(113, 3, 161)" },
  ALEPH: { icon: "/photo/work_room/Risk_Aleph.png", cssClass: "class-aleph", strip: "rgb(235, 16, 16)" }
};

async function api(path) {
  const response = await fetch(path, { credentials: "same-origin" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Ошибка запроса");
  return payload;
}

async function apiPost(path, body = {}) {
  const response = await fetch(path, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Ошибка запроса");
  return payload;
}

function ensureGameMusic(track = "selection") {
  const src = track === "brainrot" && brainrotMusicUrl
    ? brainrotMusicUrl
    : (track === "ambient" ? "/sound/ambient1.mp3" : "/sound/selection.mp3");
  const volume = track === "ambient" ? 0.28 : 0.35;
  if (!gameMusic) {
    gameMusic = new Audio(src);
    gameMusic.loop = true;
    gameMusic.volume = volume;
    gameMusic.muted = !backgroundMusicEnabled;
    backgroundMusicTrack = track;
    return gameMusic;
  }
  if (backgroundMusicTrack !== track) {
    try {
      gameMusic.pause();
      gameMusic.currentTime = 0;
    } catch (_) {}
    gameMusic = new Audio(src);
    gameMusic.loop = true;
    gameMusic.volume = volume;
    gameMusic.muted = !backgroundMusicEnabled;
    backgroundMusicTrack = track;
  }
  return gameMusic;
}

function updateGameMusicToggle() {
  if (!gameMusicToggle) return;
  gameMusicToggle.textContent = backgroundMusicEnabled ? "🔊 Музыка" : "🔇 Музыка";
  gameMusicToggle.title = backgroundMusicEnabled ? "Отключить фоновую музыку" : "Включить фоновую музыку";
  gameMusicToggle.setAttribute("aria-pressed", backgroundMusicEnabled ? "false" : "true");
  gameMusicToggle.classList.toggle("muted", !backgroundMusicEnabled);
}

function toggleGameMusic() {
  backgroundMusicEnabled = !backgroundMusicEnabled;
  window.localStorage.setItem(BACKGROUND_MUSIC_PREF, backgroundMusicEnabled ? "on" : "off");
  if (gameMusic) {
    gameMusic.muted = !backgroundMusicEnabled;
    if (backgroundMusicEnabled && !x125AudioLock && !sovuhVnActive) gameMusic.play().catch(() => {});
    else gameMusic.pause();
  }
  updateGameMusicToggle();
}

function stopGameMusic() {
  if (!gameMusic) return;
  try {
    gameMusic.pause();
    gameMusic.currentTime = 0;
  } catch (_) {}
  backgroundMusicTrack = "";
}

function showToast(label) {
  toast.textContent = `Раздел \"${label}\" пока заглушка`;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 1600);
}

function showInfoToast(text) {
  if (!text) return;
  toast.textContent = text;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 2200);
}

function playInitialEffectAnimation() {
  if (!gameRoomInitialEffect) return Promise.resolve();
  gameRoomInitialEffect.classList.remove("hidden", "playing");
  void gameRoomInitialEffect.offsetWidth;
  gameRoomInitialEffect.classList.add("playing");
  return new Promise((resolve) => {
    window.setTimeout(() => {
      gameRoomInitialEffect.classList.remove("playing");
      gameRoomInitialEffect.classList.add("hidden");
      resolve();
    }, 1220);
  });
}

function closeEventModal() {
  if (!eventOverlay) return;
  eventOverlay.classList.add("hidden");
  eventRollerWrap.classList.add("hidden");
  eventChoices.innerHTML = "";
  eventConfirmButton.classList.add("hidden");
  eventRoller.style.transition = "";
  eventRoller.style.transform = "translateY(0)";
  eventRoller.innerHTML = "";
  eventEffect.textContent = "";
  deathModalActive = false;
  if (eventModalResolver) {
    const resolve = eventModalResolver;
    eventModalResolver = null;
    resolve();
  }
}

function closeInventoryModal() {
  if (!inventoryOverlay) return;
  inventoryOverlay.classList.add("hidden");
  inventoryList.innerHTML = "";
  inventoryPreviewName.textContent = "Предмет не выбран";
  inventoryPreviewEffect.textContent = "Наведите на предмет, чтобы увидеть его эффект.";
  if (inventoryUseButton) {
    inventoryUseButton.disabled = true;
  }
  activeInventoryPayload = null;
  activeInventoryItem = null;
  if (inventoryModalResolver) {
    const resolve = inventoryModalResolver;
    inventoryModalResolver = null;
    resolve();
  }
}

function syncTrainVnPause(paused) {
  if (trainTicketButton) {
    trainTicketButton.classList.toggle("hidden", Boolean(paused) || !currentTrainTicketState?.active);
  }
  trainPauseRequest = trainPauseRequest
    .catch(() => {})
    .then(() => apiPost("/api/game/train-pause", { user_id: currentUserId(), paused: Boolean(paused) }))
    .then((payload) => {
      if (payload?.train_ticket) currentTrainTicketState = payload.train_ticket;
    })
    .catch(() => {});
}

function closeVnModal() {
  if (!vnOverlay) return;
  if (sovuhVnActive) {
    finishSovuhVnAudio();
  }
  vnOverlay.classList.add("hidden");
  syncTrainVnPause(false);
  if (vnChoices) {
    vnChoices.innerHTML = "";
  }
  if (vnHotspots) {
    vnHotspots.innerHTML = "";
  }
  if (vnObjectPrompt) {
    vnObjectPrompt.classList.add("hidden");
    vnObjectPrompt.textContent = "";
  }
  vnWindow?.classList.remove("object-scene");
  vnWindow?.classList.remove("dark-scene");
  vnPopup?.classList.add("hidden");
  if (vnText) {
    vnText.textContent = "";
  }
  if (vnCloseButton) {
    vnCloseButton.classList.add("hidden");
  }
  if (vnModalResolver) {
    const resolve = vnModalResolver;
    vnModalResolver = null;
    resolve();
  }
  if (!spectatorMode && activeRoomAnomalyId) {
    publishCameraState("room", activeRoomAnomalyId, true);
  }
}

function closeDetailsEventModal() {
  if (!detailsEventOverlay) return;
  detailsEventOverlay.classList.add("hidden");
  detailsEventChoices.innerHTML = "";
  detailsEventEffect.textContent = "";
  detailsEventConfirmButton.classList.add("hidden");
  if (detailsEventResolver) {
    const resolve = detailsEventResolver;
    detailsEventResolver = null;
    resolve();
  }
}

function showDetailsChoiceModal(config = {}) {
  if (!detailsEventOverlay) return;
  detailsEventIcon.src = config.icon || "/photo/work_room/hinthidden.png";
  detailsEventIcon.alt = config.iconAlt || "Событие";
  detailsEventIntro.textContent = config.intro || "";
  detailsEventEffect.textContent = config.effect || "";
  detailsEventChoices.innerHTML = "";
  (config.choices || []).forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "event-choice-button";
    button.textContent = choice.label;
    if (choice.title) {
      button.title = choice.title;
    }
    if (choice.disabled) {
      button.classList.add("disabled");
      button.setAttribute("aria-disabled", "true");
    } else {
      button.addEventListener("click", () => choice.onClick?.());
    }
    detailsEventChoices.appendChild(button);
  });
  if (config.confirmOnly) {
    detailsEventConfirmButton.classList.remove("hidden");
  } else {
    detailsEventConfirmButton.classList.add("hidden");
  }
  detailsEventOverlay.classList.remove("hidden");
}

function openAnomaly51NumberInput() {
  if (!detailsEventOverlay) return;
  detailsEventIcon.src = "/photo/work_room/hinthidden.png";
  detailsEventIcon.alt = "Ввод веса";
  detailsEventIntro.textContent = "Укажите свой настоящий вес";
  detailsEventEffect.textContent = "Введите число, чтобы продолжить.";
  detailsEventChoices.innerHTML = "";
  detailsEventConfirmButton.classList.add("hidden");

  const form = document.createElement("form");
  form.className = "event-number-form";

  const input = document.createElement("input");
  input.className = "event-number-input";
  input.type = "number";
  input.min = "1";
  input.max = "1000";
  input.step = "0.1";
  input.inputMode = "decimal";
  input.placeholder = "Ваш вес";
  input.required = true;
  input.autocomplete = "off";
  input.setAttribute("aria-label", "Ваш настоящий вес");

  const submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "event-choice-button";
  submit.textContent = "Подтвердить";

  form.append(input, submit);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = Number(input.value);
    if (!Number.isFinite(value) || value < 1 || value > 1000) {
      input.setCustomValidity("Введите число от 1 до 1000.");
      input.reportValidity();
      return;
    }
    input.setCustomValidity("");
    closeDetailsEventModal();
  });
  input.addEventListener("input", () => input.setCustomValidity(""));

  detailsEventChoices.appendChild(form);
  detailsEventOverlay.classList.remove("hidden");
  window.setTimeout(() => input.focus(), 0);
}

function renderInventoryPreview(item) {
  if (!item) {
    inventoryPreviewName.textContent = "Предмет не выбран";
    inventoryPreviewEffect.textContent = "Наведите на предмет, чтобы увидеть его эффект.";
    if (inventoryUseButton) {
      inventoryUseButton.disabled = true;
    }
    activeInventoryItem = null;
    return;
  }
  activeInventoryItem = item;
  inventoryPreviewName.textContent = `${item.name}${item.is_passive ? " 🛡" : ""}`;
  let previewText = item.description || "—";
  if (item.depleted) {
    previewText += `${previewText ? "\n\n" : ""}Предмет больше нельзя использовать.`;
  }
  inventoryPreviewEffect.textContent = previewText;
  if (inventoryUseButton) {
    inventoryUseButton.disabled = Boolean(item.is_passive || item.depleted || !item.can_use);
  }
}

function renderInventoryModalContent(payload) {
  if (!inventoryOverlay) return;
  activeInventoryPayload = payload || null;
  inventoryTitle.textContent = payload?.title || "Инвентарь";
  if (payload?.empty || !(payload?.items || []).length) {
    inventoryList.innerHTML = '<div class="inventory-empty">Ваш инвентарь пуст.</div>';
    renderInventoryPreview(null);
  } else {
    inventoryList.innerHTML = (payload.items || []).map((item, index) => `
      <button class="inventory-item${index === 0 ? " active" : ""}${item.special_slot === "clay" ? " clay-special-slot" : ""}" type="button" data-inventory-index="${index}">
        <div class="inventory-item-name">${escapeHtml(item.name)}${item.is_passive ? " 🛡" : ""}</div>
        <div class="inventory-item-meta">${item.special_slot === "clay" ? "Специальный слот" : `Количество: ${Number(item.amount || 0)}`}</div>
      </button>
    `).join("");
    renderInventoryPreview(payload.items[0]);
    [...inventoryList.querySelectorAll("[data-inventory-index]")].forEach((button) => {
      const index = Number(button.dataset.inventoryIndex || 0);
      const activate = () => {
        inventoryList.querySelectorAll(".inventory-item").forEach((node) => node.classList.remove("active"));
        button.classList.add("active");
        renderInventoryPreview(payload.items[index]);
      };
      button.addEventListener("mouseenter", activate);
      button.addEventListener("focus", activate);
      button.addEventListener("click", activate);
    });
  }
}

function showInventoryModal(payload) {
  if (!inventoryOverlay) return Promise.resolve();
  renderInventoryModalContent(payload);
  inventoryOverlay.classList.remove("hidden");
  return new Promise((resolve) => {
    inventoryModalResolver = resolve;
  });
}

async function openInventoryModal() {
  const payload = await api(`/api/game/inventory?user_id=${currentUserId()}`);
  await showInventoryModal(payload);
}

async function openProtocolXTargetChoice() {
  const protocol = activeRoomPayload?.protocol_x || {};
  if (!protocol.owned) return;
  if (!protocol.available) {
    showInfoToast(protocol.used_today ? "Протокол X уже использован сегодня." : "Сейчас нет доступных целей для саботажа.");
    return;
  }
  showEventChoiceModal({
    intro: "Протокол X",
    effect: "Выберите живую цель для случайного саботажа.",
    icon: "/photo/work_room/hinthidden.png",
    choices: (protocol.targets || []).map((target) => ({
      label: target.name || `Игрок ${target.id}`,
      onSelect: async () => {
        try {
          const payload = await apiPost("/api/game/protocol-x", {
            user_id: currentUserId(),
            target_id: target.id
          });
          closeEventModal();
          if (activeRoomAnomalyId) {
            const refreshed = await api(`/api/work-room?user_id=${currentUserId()}&anomaly_id=${activeRoomAnomalyId}`);
            if (refreshed.room) renderWorkRoom(refreshed.room);
          }
          await showInfoModal("Протокол X", payload.message || "Саботаж выполнен.");
        } catch (error) {
          closeEventModal();
          await showRuntimeErrorModal(error);
        }
      }
    }))
  });
}

async function useInventoryItem() {
  if (!activeInventoryItem || inventoryUseBusy) return;
  inventoryUseBusy = true;
  try {
    const payload = await apiPost("/api/game/use-item", {
      user_id: currentUserId(),
      item_id: activeInventoryItem.id
    });
    if (payload.doomsday_vn) {
      closeInventoryModal();
      await startDoomsdaySecretVn();
      return;
    }
    if (payload.clay_transfer?.pending) {
      closeInventoryModal();
      showEventChoiceModal({
        icon: "/photo/work_room/neutralresult.png",
        iconAlt: "Глиняная статуя",
        intro: "Передать Глиняную статую",
        effect: "Выберите живого игрока. Статуя занимает отдельный специальный слот, поэтому свободная обычная ячейка не требуется.",
        choices: [
          ...(payload.clay_transfer.candidates || []).map((candidate) => ({
            label: candidate.name || `Игрок ${candidate.id}`,
            onSelect: async () => {
              try {
                const transfer = await apiPost("/api/game/clay-transfer", {
                  user_id: currentUserId(),
                  target_id: candidate.id
                });
                closeEventModal();
                if (transfer.item_result?.modal) {
                  await showInfoModal(
                    transfer.item_result.modal.intro || "Глиняная статуя",
                    transfer.item_result.modal.effect || transfer.item_result.description || "Статуя передана."
                  );
                }
              } catch (error) {
                await showRuntimeErrorModal(error);
              }
            }
          })),
          { label: "Отмена", onSelect: closeEventModal }
        ]
      });
      return;
    }
    if (payload.room) {
      activeRoomPayload = payload.room;
      renderWorkRoom(payload.room);
    }
    if (payload.inventory) {
      activeInventoryPayload = payload.inventory;
      renderInventoryModalContent(payload.inventory);
      inventoryOverlay.classList.remove("hidden");
    }
    if (payload.message) {
      showInfoToast(payload.message);
    }
    if (payload.game_state && !payload.doomsday_vn) {
      await applyGameState(payload.game_state, { forceRefresh: true });
    }
    if (payload.damage) {
      applyDamageFeedback(payload);
      if (payload.damage.shield_triggered) await showDeathShieldMiracleModal(payload.damage);
    }
    if (payload.item_result?.modal) {
      await showInfoModal(
        payload.item_result.modal.intro || payload.item_result.title || "Предмет использован",
        payload.item_result.modal.effect || payload.item_result.description || "",
        {
          iconSrc: payload.item_result.modal.icon || payload.item_result.modal.iconSrc || "/photo/work_room/success.png",
          iconAlt: payload.item_result.modal.iconAlt || "Предмет"
        }
      );
    } else if (payload.item_result?.description) {
      await showInfoModal(payload.item_result.title || "Предмет использован", payload.item_result.description);
    }
    if (payload.player_dead) {
      closeInventoryModal();
      await showDeathModal(payload.death_reason || "Сотрудник погиб при использовании предмета.");
      if (showFinalResults(payload.final_results || payload.game_state?.final_results)) return;
      if (payload.game_state?.game?.started) await applyGameState(payload.game_state, { forceRefresh: true });
    }
  } finally {
    inventoryUseBusy = false;
  }
}

// Edit DOOMSDAY_SECRET_DIALOGUE to extend or rewrite the day-15 secret scene.
// speaker accepts "unknown" (left portrait) or "angela" (right portrait).
const DOOMSDAY_SECRET_DIALOGUE = [
  { speaker: "unknown", name: "???", text: "Как проходит работа, Анжела?" },
  { speaker: "angela", name: "Анжела", text: "Все согласно плану" },
  { speaker: "unknown", name: "???", text: "Прекрасно. Хм... Похоже, у нас гости. Ты свободна, можешь идти." },
  { speaker: "angela", name: "Анжела", text: "Хорошо, если что-то понадобится - я рядом." },
  { speaker: "unknown", name: "???", text: "Тебя здесь не должно быть, но раз уж ты попал сюда, то, видимо, воспользовался одним из аномальных артефактов. Интересно." },
  { speaker: "unknown", name: "???", text: "Позволь представиться, я Z, либо можешь просто называть меня Архитектор." },
  { speaker: "unknown", name: "Архитектор", text: "После того, как предыдущий управляющий отошел от дел, мне вручили комплекс во временное управление. Моя задача - найти достойного преемника." },
  { speaker: "unknown", name: "Архитектор", text: "Твой пытливый ум неплохо скрасит твоё резюме. Но для окончательного решения в твою пользу этого пока мало. Изучи все аномалии, затем отправляйся в реальный комплекс." },
  { speaker: "unknown", name: "Архитектор", text: "Хмм? Ты думал, что аномалии, с которыми ты работал ранее настоящие? Это всего лишь симуляция, можно сказать даже упрощённая. Настоящее испытание будет дальше." },
  { speaker: "unknown", name: "Архитектор", text: "Не разочаруй меня. В нашу следующую встречу я буду ждать от тебя выдаюшихся результатов. А теперь прощай." }
];

async function startDoomsdaySecretVn() {
  const resumeBackgroundMusic = Boolean(gameMusic && !gameMusic.paused && backgroundMusicEnabled);
  if (gameMusic) gameMusic.pause();
  const secretMusic = new Audio("/sound/Lobotomy%20Corporation%20OST%20-%20Story%2004.mp3");
  secretMusic.loop = true;
  secretMusic.volume = 0.55;
  if (backgroundMusicEnabled) secretMusic.play().catch(() => {});
  const stopSecretMusic = () => {
    secretMusic.pause();
    secretMusic.currentTime = 0;
    if (resumeBackgroundMusic && gameMusic && backgroundMusicEnabled) gameMusic.play().catch(() => {});
  };
  let overlay = document.getElementById("doomsdaySecretVn");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "doomsdaySecretVn";
    overlay.className = "doomsday-secret-vn";
    overlay.innerHTML = `
      <div class="doomsday-secret-stage">
        <img class="doomsday-secret-bg" src="/photo/VN/secretscene.png" alt="Секретная сцена">
        <img class="doomsday-secret-portrait unknown" src="/photo/VN/architector.png" alt="???">
        <img class="doomsday-secret-portrait angela" src="/photo/VN/angela.png" alt="Анжела">
        <div class="doomsday-secret-textbox">
          <div class="doomsday-secret-name"></div>
          <div class="doomsday-secret-text"></div>
          <button class="doomsday-secret-next" type="button">ДАЛЕЕ</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
  }
  const left = overlay.querySelector(".doomsday-secret-portrait.unknown");
  const right = overlay.querySelector(".doomsday-secret-portrait.angela");
  const name = overlay.querySelector(".doomsday-secret-name");
  const text = overlay.querySelector(".doomsday-secret-text");
  const next = overlay.querySelector(".doomsday-secret-next");
  let index = 0;
  overlay.classList.remove("hidden");
  const render = () => {
    const line = DOOMSDAY_SECRET_DIALOGUE[index];
    name.textContent = line.name;
    text.textContent = line.text;
    left.classList.toggle("dimmed", line.speaker !== "unknown");
    right.classList.toggle("dimmed", line.speaker !== "angela");
    const lastAngelaLine = DOOMSDAY_SECRET_DIALOGUE.reduce((last, item, itemIndex) => item.speaker === "angela" ? itemIndex : last, -1);
    right.classList.toggle("departed", index > lastAngelaLine);
    next.textContent = index === DOOMSDAY_SECRET_DIALOGUE.length - 1 ? "ЗАВЕРШИТЬ" : "ДАЛЕЕ";
  };
  render();
  await new Promise((resolve, reject) => {
    next.onclick = async () => {
      if (index < DOOMSDAY_SECRET_DIALOGUE.length - 1) {
        index += 1;
        render();
        return;
      }
      next.disabled = true;
      try {
        const payload = await apiPost("/api/game/doomsday-vn-complete", { user_id: currentUserId() });
        overlay.classList.add("hidden");
        stopSecretMusic();
        if (payload.game_state) await applyGameState(payload.game_state, { forceRefresh: true });
        resolve();
      } catch (error) {
        stopSecretMusic();
        next.disabled = false;
        reject(error);
      }
    };
  });
}

function showDetailsInfoModal(config = {}) {
  if (!detailsEventOverlay) return Promise.resolve();
  detailsEventResolver = null;
  showDetailsChoiceModal({
    icon: config.icon,
    iconAlt: config.iconAlt,
    intro: config.intro || "",
    effect: config.effect || "",
    confirmOnly: true,
    choices: []
  });
  return new Promise((resolve) => {
    detailsEventResolver = resolve;
  });
}

function normalizeCompanionOffer(offer = null) {
  if (!offer || !offer.pending) return null;
  return {
    hintIndex: Number(offer.hint_index || 0),
    companionId: Number(offer.companion_id || 0),
    displayName: offer.display_name || currentDetailsPayload?.base_info?.code_name || "SC-UN-U-0",
    canAccept: Boolean(offer.can_accept),
    blockedReason: offer.blocked_reason || "",
    modal: offer.modal || {
      intro: "Новый компаньон",
      effect: `Вам предложена аномалия ${offer.display_name || "SC-UN-U-0"} в качестве компаньона. В случае отказа - дальнейшее исследование невозможно.`,
      icon: "/photo/work_room/goodresult.png",
      iconAlt: "Новый компаньон"
    }
  };
}

async function openCompanionOfferModal(offer) {
  const normalized = normalizeCompanionOffer(offer);
  if (!normalized || !activeRoomAnomalyId) return;
  await new Promise((resolve) => {
    detailsEventResolver = resolve;
    showDetailsChoiceModal({
      icon: normalized.modal.icon || "/photo/work_room/goodresult.png",
      iconAlt: normalized.modal.iconAlt || "Новый компаньон",
      intro: normalized.modal.intro || "Новый компаньон",
      effect: normalized.modal.effect || "",
      choices: [
        {
          label: "Да",
          disabled: !normalized.canAccept,
          title: normalized.canAccept ? "" : (normalized.blockedReason || "нельзя сменить имеющегося компаньона"),
          onClick: async () => {
            try {
              const payload = await apiPost("/api/details/companion-accept", {
                user_id: currentUserId(),
                anomaly_id: activeRoomAnomalyId
              });
              if (payload.room) {
                activeRoomPayload = payload.room;
              }
              renderDetailsScreen(payload.details);
              if (payload.room) {
                renderWorkRoom(payload.room);
              }
            } finally {
              if (detailsEventResolver) {
                const resolver = detailsEventResolver;
                detailsEventResolver = null;
                detailsEventOverlay.classList.add("hidden");
                resolver();
              }
            }
          }
        },
        {
          label: "Отказаться",
          onClick: async () => {
            try {
              const payload = await apiPost("/api/details/companion-decline", {
                user_id: currentUserId(),
                anomaly_id: activeRoomAnomalyId
              });
              if (payload.room) {
                activeRoomPayload = payload.room;
              }
              renderDetailsScreen(payload.details);
              if (payload.room) {
                renderWorkRoom(payload.room);
              }
            } finally {
              if (detailsEventResolver) {
                const resolver = detailsEventResolver;
                detailsEventResolver = null;
                detailsEventOverlay.classList.add("hidden");
                resolver();
              }
            }
          }
        }
      ]
    });
  });
}

async function runNubertDialog(codeName) {
  await new Promise((resolve) => {
    detailsEventResolver = resolve;
    showDetailsChoiceModal({
      intro: `${codeName}: Ты меня любишь?`,
      effect: "Выберите ответ.",
      choices: [
        {
          label: "Да",
          onClick: () => {
            showDetailsChoiceModal({
              intro: `${codeName}: Ой, что-то я заговорился. Тебе, наверное, пора?`,
              effect: "Последствие: -5 SP",
              choices: [
                {
                  label: "Нет",
                  onClick: () => {
                    showDetailsChoiceModal({
                      intro: `${codeName}: Хе-хе. Тогда давай еще кое-что расскажу...`,
                      effect: "Последствие: еще -5 SP",
                      choices: [
                        {
                          label: "Пнуть Нуберта",
                          onClick: () => {
                            showDetailsChoiceModal({
                              intro: `${codeName}: ААААААЙ!`,
                              effect: "Последствие: -10 SP",
                              choices: [],
                              confirmOnly: true
                            });
                          }
                        },
                        {
                          label: "Уйти",
                          onClick: () => {
                            showDetailsChoiceModal({
                              intro: `${codeName}: ...`,
                              effect: "Диалог завершен.",
                              choices: [],
                              confirmOnly: true
                            });
                          }
                        }
                      ]
                    });
                  }
                },
                {
                  label: "Да",
                  onClick: () => {
                    showDetailsChoiceModal({
                      intro: `${codeName}: Ну тогда иди.`,
                      effect: "Диалог завершен.",
                      choices: [],
                      confirmOnly: true
                    });
                  }
                }
              ]
            });
          }
        },
        {
          label: "Нет",
          onClick: () => {
            showDetailsChoiceModal({
              intro: `${codeName}: Но... но...`,
              effect: "Тебе как-то мерзко на душе. Диалог завершен.",
              choices: [],
              confirmOnly: true
            });
          }
        }
      ]
    });
  });
}

function showVnInteractionModal(config = {}) {
  if (!vnOverlay) return Promise.resolve();
  vnWindow?.classList.remove("character-hidden", "vn-scene-fade-out", "vn-scene-fade-in");
  vnNameplate.textContent = config.codeName || "SC-NA-Z-0";
  vnSpeaker.textContent = config.speaker || "VN_anomaly";
  vnPortrait.src = config.portrait || "/photo/VN/VN_anomaly.png";
  vnPortrait.alt = config.speaker || "VN_anomaly";
  if (vnBg) {
    if (config.background) {
      vnBg.classList.remove("hidden");
      vnBg.src = config.background;
    } else {
      vnBg.classList.add("hidden");
      vnBg.removeAttribute("src");
    }
  }
  if (vnText) {
    vnText.textContent = "";
  }
  if (vnChoices) {
    vnChoices.innerHTML = "";
  }
  if (vnCloseButton) {
    vnCloseButton.classList.remove("hidden");
  }
  vnOverlay.classList.remove("hidden");
  syncTrainVnPause(true);
  publishVnCameraState({
    ...config,
    nameplate: config.codeName || "SC-NA-Z-0",
    text: config.text || "",
    confirmOnly: true,
  }, false);
  return new Promise((resolve) => {
    vnModalResolver = resolve;
  });
}

function typewriteVnText(text = "", speed = 22, generation = vnTextGeneration) {
  if (!vnText) return Promise.resolve();
  vnText.textContent = "";
  return new Promise((resolve) => {
    let index = 0;
    const source = String(text || "");
    const tick = () => {
      if (generation !== vnTextGeneration) {
        resolve();
        return;
      }
      if (index >= source.length) {
        resolve();
        return;
      }
      vnText.textContent += source[index];
      index += 1;
      window.setTimeout(tick, speed);
    };
    tick();
  });
}

function showVnChoiceModal(config = {}) {
  if (!vnOverlay) return Promise.resolve();
  const textGeneration = ++vnTextGeneration;
  const objectScene = (Array.isArray(config.hotspots) && config.hotspots.length > 0) || Boolean(config.visualOnly);
  vnWindow?.classList.toggle("object-scene", objectScene);
  vnWindow?.classList.toggle("dark-scene", Boolean(config.darkScene));
  vnWindow?.classList.toggle("character-hidden", config.characterVisible === false);
  vnWindow?.classList.toggle("portrait-hidden", config.portraitVisible === false);
  vnWindow?.classList.toggle("nameplate-hidden", config.nameplateVisible === false);
  vnPopup?.classList.add("hidden");
  let sceneTime = vnWindow?.querySelector(".vn-scene-time");
  if (vnWindow && !sceneTime) {
    sceneTime = document.createElement("div");
    sceneTime.className = "vn-scene-time hidden";
    vnWindow.appendChild(sceneTime);
  }
  if (sceneTime) {
    sceneTime.textContent = config.sceneTime || "";
    sceneTime.classList.toggle("hidden", !config.sceneTime);
  }
  vnNameplate.textContent = config.nameplate === "" ? "" : (config.nameplate || "Аномалия");
  vnSpeaker.textContent = config.speaker || "";
  vnPortrait.src = config.portrait || "/photo/VN/VN_anomaly.png";
  vnPortrait.alt = config.speaker || "Аномалия";
  if (vnBg) {
    if (config.background) {
      vnBg.classList.remove("hidden");
      vnBg.src = config.background;
      vnBg.style.objectFit = config.backgroundStyle?.objectFit || "cover";
      vnBg.style.width = config.backgroundStyle?.width || "100%";
      vnBg.style.height = config.backgroundStyle?.height || "100%";
      vnBg.style.left = config.backgroundStyle?.left || "0";
      vnBg.style.top = config.backgroundStyle?.top || "0";
    } else {
      vnBg.classList.add("hidden");
      vnBg.removeAttribute("src");
    }
  }
  if (vnChoices) {
    vnChoices.innerHTML = "";
  }
  if (vnHotspots) {
    vnHotspots.innerHTML = "";
  }
  if (vnObjectPrompt) {
    const promptText = objectScene ? (config.objectPrompt || config.text || "") : "";
    vnObjectPrompt.textContent = promptText;
    vnObjectPrompt.classList.toggle("hidden", !objectScene || !promptText);
  }
  if (vnText) {
    vnText.textContent = "";
  }
  if (vnCloseButton) {
    vnCloseButton.classList.toggle("hidden", !config.confirmOnly);
    vnCloseButton.textContent = config.confirmLabel || "ОК";
  }
  vnOverlay.classList.remove("hidden");
  syncTrainVnPause(true);
  publishVnCameraState(config, objectScene);
  return new Promise((resolve) => {
    vnModalResolver = resolve;
    if (objectScene && vnHotspots) {
      config.hotspots.forEach((hotspot) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `vn-hotspot${hotspot.className ? ` ${hotspot.className}` : ""}`;
        button.setAttribute("aria-label", hotspot.label || "Интерактивный объект");
        button.style.left = hotspot.left;
        button.style.top = hotspot.top;
        button.style.width = hotspot.width;
        button.style.height = hotspot.height;
        const label = document.createElement("span");
        label.textContent = hotspot.label || "Осмотреть";
        button.appendChild(label);
        button.addEventListener("click", () => hotspot.onClick?.());
        vnHotspots.appendChild(button);
      });
      return;
    }
    typewriteVnText(config.text || "", config.speed || 22, textGeneration).then(() => {
      if (textGeneration !== vnTextGeneration) return;
      if (config.confirmOnly) {
        return;
      }
      let dialogInput = null;
      if (config.input) {
        dialogInput = document.createElement(config.input.multiline ? "textarea" : "input");
        dialogInput.className = "vn-dialog-input";
        dialogInput.placeholder = config.input.placeholder || "";
        dialogInput.maxLength = Number(config.input.maxLength || 200);
        vnChoices.appendChild(dialogInput);
      }
      (config.choices || []).forEach((choice) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "vn-choice-button";
        button.textContent = choice.label;
        if (choice.title) {
          button.title = choice.title;
        }
        if (choice.disabled) {
          button.classList.add("disabled");
          button.setAttribute("aria-disabled", "true");
        } else {
          button.addEventListener("click", () => choice.onClick?.(dialogInput?.value || ""));
        }
        vnChoices.appendChild(button);
      });
    });
  });
}

function closeVnPopup() {
  vnPopup?.classList.add("hidden");
  if (vnPopupActions) vnPopupActions.innerHTML = "";
  publishCurrentVnDomState();
}

function showVnPopup(text, choices = [{ label: "Закрыть", onClick: closeVnPopup }]) {
  if (!vnPopup || !vnPopupText || !vnPopupActions) return;
  vnPopupText.textContent = text || "";
  vnPopupActions.innerHTML = "";
  choices.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "vn-choice-button";
    button.textContent = choice.label;
    button.addEventListener("click", () => choice.onClick?.());
    vnPopupActions.appendChild(button);
  });
  vnPopup.classList.remove("hidden");
  publishCurrentVnDomState(text, choices.map((choice) => choice?.label || ""));
}

function playVnAudio(src) {
  try {
    const audio = new Audio(src);
    audio.volume = 0.85;
    audio.__playFailed = false;
    audio.play().catch(() => { audio.__playFailed = true; });
    return audio;
  } catch (_) {
    return null;
  }
}

const SOVUH_VN_ROOT = "/photo/VN/sova";
let sovuhVnActive = false;
let sovuhResumeBackgroundMusic = false;
let sovuhRoomTimer = null;
let sovuhRoomSeconds = 0;
const sovuhVnAudio = new Set();

function sovuhAsset(name) {
  return `${SOVUH_VN_ROOT}/${encodeURIComponent(name)}`;
}

function sovuhSound(name, volume = 0.85) {
  const src = `/sound/${encodeURIComponent(name)}`;
  const audio = playVnAudio(src);
  if (audio) {
    audio.volume = volume;
    sovuhVnAudio.add(audio);
    audio.addEventListener("ended", () => sovuhVnAudio.delete(audio), { once: true });
  }
  return audio;
}

function clearSovuhRoomTimer() {
  if (sovuhRoomTimer) window.clearInterval(sovuhRoomTimer);
  sovuhRoomTimer = null;
  sovuhRoomSeconds = 0;
}

function beginSovuhVnAudio() {
  sovuhVnActive = true;
  sovuhResumeBackgroundMusic = Boolean(gameMusic && !gameMusic.paused && backgroundMusicEnabled);
  if (gameMusic) gameMusic.pause();
}

function finishSovuhVnAudio() {
  clearSovuhRoomTimer();
  sovuhVnAudio.forEach((audio) => {
    try { audio.pause(); } catch (_) {}
  });
  sovuhVnAudio.clear();
  const shouldResume = sovuhResumeBackgroundMusic;
  sovuhVnActive = false;
  sovuhResumeBackgroundMusic = false;
  if (shouldResume && gameMusic && backgroundMusicEnabled && !x125AudioLock) {
    gameMusic.play().catch(() => {});
  }
}

function sovuhVnConfig(text, choices = [], options = {}) {
  return {
    nameplate: options.nameplate || "",
    nameplateVisible: Boolean(options.nameplate),
    speaker: "",
    portrait: "",
    portraitVisible: false,
    background: options.darkScene ? null : (options.background || null),
    backgroundStyle: options.backgroundStyle || null,
    sceneTime: options.sceneTime || "",
    darkScene: Boolean(options.darkScene),
    text,
    choices,
    hotspots: options.hotspots || [],
    objectPrompt: options.objectPrompt || "",
    confirmOnly: Boolean(options.confirmOnly),
    confirmLabel: options.confirmLabel || "Продолжить",
    speed: 18
  };
}

async function resolveSovuhZombieAction(action) {
  const payload = await apiPost("/api/game/sovuh-zombie-action", {
    user_id: currentUserId(),
    anomaly_id: 32,
    action
  });
  if (payload.room) {
    renderWorkRoom(payload.room);
  }
  if (payload.outcome === "death" || payload.player_dead) {
    closeVnModal();
    await showDeathModal(payload.death_reason || "Сова-зомби настигла сотрудника.");
    if (showFinalResults(payload.final_results || payload.game_state?.final_results)) {
      return;
    }
    if (payload.game_state?.game?.started) {
      await applyGameState(payload.game_state, { forceRefresh: true });
      return;
    }
    closeGameScreen();
    closeOnlineScreen();
    closePlayScreen();
    return;
  }
  if (payload.outcome === "completed") {
    closeVnModal();
  }
}

function renderSovuhZombieScene(step, blockIndex = 0) {
  const go = (nextStep) => () => renderSovuhZombieScene(nextStep);
  const lethal = (action) => () => resolveSovuhZombieAction(action).catch((error) => showRuntimeErrorModal(error));
  const scene = (name) => sovuhAsset(`${name}.png`);
  const playerName = discordUser?.global_name || discordUser?.username || "сотрудник";
  const dialogueSequences = {
    helicopter: {
      background: scene("scene_helicopter"),
      next: "roof",
      blocks: [
        { speaker: "Пилот", text: "Итак, народ. Мы прибыли на место. Высаживаю вас на крыше. Вернусь к вам не раньше чем через 2 часа." },
        { speaker: "Пилот", text: "Ваша задача — исследовать объект и выяснить, что стало источником всплеска подозрительной активности. Удачи." }
      ]
    },
    roof: {
      background: scene("scene_roof"),
      time: "12:45",
      next: "stairs",
      blocks: [
        { text: "Крыша неизвестного здания." },
        { speaker: "Эпсилон-3", text: "Опять послали в какую-то глушь. Что это за задание вообще? Что мы ищем?" },
        { speaker: "Эпсилон-1", text: "Небось опять какой-то придурок решил украсть у корпорации аномальный прибор и, даже не зная, что он делает, запустил его и стал кучкой плоти, жаждущей крови." },
        { speaker: "Эпсилон-3", text: "А почему вообще нас отправили этим заниматься? Неужели нельзя было кроликов отправить? За что им платят?" },
        { speaker: "Эпсилон-1", text: "Мне по барабану. Всё лучше, чем торчать в комплексе." },
        { speaker: "Эпсилон-2", text: "Хорош трепаться, давайте за дело." }
      ]
    },
    stairs: {
      background: scene("scene_stairs"),
      time: "12:46",
      next: "hall",
      blocks: [
        { text: "Затхлый запах сырости и пыли. Кроме крыс здесь явно никто не жил последние лет 10. Ржавые ступени издавали неприятные звуки и слегка прогибались под весом людей, идущих впереди." },
        { speaker: "Эпсилон-1", text: "Что показывает датчик?" },
        { speaker: "Эпсилон-3", text: "Есть сигнатура примерно на пятом этаже. Придется спускаться. Пока мы летели, я насчитал тут 15 этажей." },
        { speaker: "Эпсилон-3", text: "Да твою же мать, и спрашивается, зачем нас на крыше высаживали, нельзя было внизу оставить?" },
        { text: "Голоса отдалялись, и вы решили догнать команду." }
      ]
    },
    hall: {
      background: scene("scene_hall"),
      time: "13:01",
      blocks: [
        { text: "Вы не вслушивались в дальнейшие разговоры. Идя, можно сказать, на автомате, вы дошли до коридора где-то около 8 этажа. Лестница вниз через пожарный проход оказалась разрушена, и потом вы с командой шли по коридору, ища другой проход." },
        { text: "Зачем корпорация направила сюда и вас? Вы не полевой агент, а исследователь, который работает в комплексе...\n\nОт мыслей вас отвлек чей-то голос." },
        { speaker: "Эпсилон-1", text: "Эй, новичок, а тебя за что сюда впрягли? Ты же работал прямо в научном корпусе? Исследовал аномалии?" },
        { speaker: "Эпсилон-3", text: "Видимо, плохо работал." },
        { speaker: "Эпсилон-1", text: `Хе-хе-хе. Ну да, сюда точно не за выдающуюся работу отправляют. Ну так что, ${playerName}?`, choices: [
          { label: "Самому хотелось бы знать", next: "hallAnswer" },
          { label: "Отправили и отправили, чо жаловаться-то уже", next: "hallAnswer" }
        ] }
      ]
    },
    hallAnswer: {
      background: scene("scene_hall"), time: "13:01", next: "hall2",
      blocks: [{ speaker: "Эпсилон-1", text: "Значит, тоже не в курсе. Ну, есть у меня одна мыслишка, почему тебя тоже послали." }]
    },
    hall2: {
      background: scene("scene_hall2"), time: "13:10", next: "hall3",
      blocks: [
        { text: "Очередной коридор, только уже без окон. Пахнет свежей кровью." },
        { speaker: "Эпсилон-3", text: "Какого хера тут вообще происходит?" },
        { speaker: "Эпсилон-1", text: "Эх, видимо, тут реально какая-то мутировавшая хренотень живет. В прошлый раз я месяц лежал в санчасти, пока гнойники от укуса той дряни не сошли с моей руки..." },
        { text: "Сотрудник остановился и уставился на дверь." },
        { speaker: "Эпсилон-3", text: "Сигнатура где-то в этой стороне, приготовьтесь." }
      ]
    },
    hall4: {
      background: scene("scene_hall4"), time: "13:16", next: "breach",
      blocks: [
        { speaker: "Эпсилон-3", text: "Наш объект в 40 метрах от нас на запад. Постойте, 35... 30? Что за чертовщина?" },
        { text: "В его голосе скрывался неподдельный ужас. Ситуация явно нештатная и выходит за рамки привычных вылазок на подобных миссиях." },
        { speaker: "Эпсилон-3", text: "25... 20... 10... 5..." },
        { text: "Остальные подняли оружие и начали следить. Вы прижались к стене." },
        { speaker: "Эпсилон-3", text: "Хмм... тут стена и прохода нет. Нет, тут точно нет комнаты. Прибор, похоже, сбоит. Нужно сообщить..." }
      ]
    },
    room: {
      background: scene("scene_room"), time: "13:30", next: "roomChoice",
      blocks: [
        { text: "Вы нашли комнату с огромной тяжёлой металлической дверью и закрыли её. Есть время перевести дух..." },
        { speaker: "???", text: `${playerName}, открой!` },
        { text: "Этот голос вывел вас из раздумий. Он звучал прямо как голос Эпсилона-3." },
        { speaker: "Эпсилон-3", text: "Быстрей открой, та хрень явно не подохла от пуль, но пока валяется где-то там." }
      ]
    },
    doorOpen: {
      background: scene("scene_door_open"),
      blocks: [
        { text: "Дверь окончательно раскрылась, и стало ясно, что бежать некуда." },
        { speaker: "???", text: "А вот и последний.", action: "door" }
      ]
    },
    cabinet: {
      background: scene("scene_door_blocked"), next: "cabinetDeath",
      blocks: [
        { text: "Это явно не его голос. Тот сотрудник не мог выжить." },
        { speaker: "Эпсилон-3", text: "Умоляю, впусти меня. Он уже близко." },
        { text: "Не слушай его, это ловушка." },
        { speaker: "Эпсилон-3", text: `${playerName}!` },
        { text: "Вы закончили с баррикадой, ничто не пройдет внутрь." },
        { speaker: "???", text: "Да уж, заставил ты меня повозиться. Не хочешь впускать сам? Тогда не жди, что всё кончится быстро." }
      ]
    },
    cabinetDeath: {
      background: scene("scene_door_slammed"),
      blocks: [
        { speaker: "???", text: "Ку-ку." },
        { text: "Это конец. От чудовища вас отделяют лишь остатки двери. Скоро оно прорвется...", action: "cabinet" }
      ]
    },
    chaseText: {
      darkScene: true, next: "chase",
      blocks: [
        { text: "Вы шли на источник звука, но так и не смогли разглядеть вертолёт." },
        { speaker: "???", text: "Ищешь что-то?" },
        { text: "Вы обернулись на источник голоса." },
        { speaker: "???", text: "Долго же мне пришлось за тобой бегать." },
        { text: "Эта... тварь... Это она издавала звуки..." }
      ]
    }
  };
  const sequence = dialogueSequences[step];
  if (sequence) {
    const block = sequence.blocks[Math.max(0, Math.min(blockIndex, sequence.blocks.length - 1))];
    const isLast = blockIndex >= sequence.blocks.length - 1;
    let choices;
    if (block.choices) {
      choices = block.choices.map((choice) => ({ label: choice.label, onClick: go(choice.next) }));
    } else if (block.action) {
      choices = [{ label: "Завершить", onClick: lethal(block.action) }];
    } else {
      choices = [{
        label: isLast ? "Продолжить" : "Далее",
        onClick: isLast ? go(sequence.next) : () => renderSovuhZombieScene(step, blockIndex + 1)
      }];
    }
    if (step === "helicopter" && blockIndex === 0) sovuhSound("Helicopter Sound Effect.mp3", 0.75);
    showVnChoiceModal(sovuhVnConfig(block.text, choices, {
      nameplate: block.speaker || "",
      background: sequence.background || null,
      darkScene: Boolean(sequence.darkScene),
      sceneTime: sequence.time || ""
    }));
    return;
  }
  const scenes = {
    intro: sovuhVnConfig(
      "Район нижнего дистрикта №10. Получено сообщение о всплеске аномальной активности в области.\n\nВыслан вооруженный отряд Эпсилон-1",
      [{ label: "Продолжить", onClick: go("helicopter") }],
      { darkScene: true, sceneTime: "18:43" }
    ),
    helicopter: sovuhVnConfig(
      "Пилот: Итак, народ. Мы прибыли на место. Высаживаю вас на крыше. Вернусь к вам не раньше чем через 2 часа.\n\nВаша задача — исследовать объект и выяснить, что стало источником всплеска подозрительной активности. Удачи.",
      [{ label: "Продолжить", onClick: go("roof") }],
      { background: scene("scene_helicopter") }
    ),
    roof: sovuhVnConfig(
      "18:45 — крыша неизвестного здания\n\nЭпсилон-3: Опять послали в какую-то глушь. Что это за задание вообще? Что мы ищем?\n\nЭпсилон-1: Небось опять какой-то придурок решил украсть у корпорации аномальный прибор и, даже не зная, что он делает, запустил его и стал кучкой плоти, жаждущей крови.\n\nЭпсилон-3: А почему вообще нас отправили этим заниматься? Неужели нельзя было кроликов отправить? За что им платят?\n\nЭпсилон-1: Мне по барабану. Всё лучше, чем торчать в комплексе.\n\nЭпсилон-2: Хорош трепаться, давайте за дело.",
      [{ label: "Продолжить", onClick: go("stairs") }],
      { background: scene("scene_roof") }
    ),
    stairs: sovuhVnConfig(
      "18:46\n\nЗатхлый запах сырости и пыли. Кроме крыс здесь явно никто не жил последние лет 10. Ржавые ступени издавали неприятные звуки и слегка прогибались под весом людей, идущих впереди.\n\nЭпсилон-1: Что показывает датчик?\n\nЭпсилон-3: Есть сигнатура примерно на пятом этаже. Придется спускаться. Пока мы летели, я насчитал тут 15 этажей.\n\nЭпсилон-3: Да твою же мать, и спрашивается, зачем нас на крыше высаживали, нельзя было внизу оставить?\n\nГолоса отдалялись, и вы решили догнать команду.",
      [{ label: "Продолжить", onClick: go("hall") }],
      { background: scene("scene_stairs") }
    ),
    hall: sovuhVnConfig(
      `19:01\n\nВы не вслушивались в дальнейшие разговоры. Идя, можно сказать, на автомате, вы дошли до коридора где-то около 8 этажа. Лестница вниз через пожарный проход оказалась разрушена, и потом вы с командой шли по коридору, ища другой проход.\n\nЗачем корпорация направила сюда и вас? Вы не полевой агент, а исследователь, который работает в комплексе...\n\nОт мыслей вас отвлек чей-то голос.\n\nЭпсилон-1: Эй, новичок, а тебя за что сюда впрягли? Ты же работал прямо в научном корпусе? Исследовал аномалии?\n\nЭпсилон-3: Видимо, плохо работал.\n\nЭпсилон-1: Хе-хе-хе. Ну да, сюда точно не за выдающуюся работу отправляют. Ну так что, ${playerName}?`,
      [
        { label: "Самому хотелось бы знать", onClick: go("hallAnswer") },
        { label: "Отправили и отправили, чо жаловаться-то уже", onClick: go("hallAnswer") }
      ],
      { background: scene("scene_hall") }
    ),
    hallAnswer: sovuhVnConfig(
      "Эпсилон-1: Значит, тоже не в курсе. Ну, есть у меня одна мыслишка, почему тебя тоже послали.",
      [{ label: "Продолжить", onClick: go("hall2") }],
      { background: scene("scene_hall") }
    ),
    hall2: sovuhVnConfig(
      "19:10\n\nОчередной коридор, только уже без окон. Пахнет свежей кровью.\n\nЭпсилон-3: Какого хера тут вообще происходит?\n\nЭпсилон-1: Эх, видимо, тут реально какая-то мутировавшая хренотень живет. В прошлый раз я месяц лежал в санчасти, пока гнойники от укуса той дряни не сошли с моей руки...\n\nСотрудник остановился и уставился на дверь.\n\nЭпсилон-3: Сигнатура где-то в этой стороне, приготовьтесь.",
      [{ label: "Продолжить", onClick: go("hall3") }],
      { background: scene("scene_hall2") }
    ),
    hall3: sovuhVnConfig(
      "Тишину в коридоре нарушают только еле слышные шаги и омерзительный хлюпающий звук при шагах по лужам красного цвета.\n\nВаши коллеги перестали разговаривать и явно сосредоточились на том, что вас может ждать впереди.",
      [{ label: "Продолжить", onClick: go("hall4") }],
      { background: scene("scene_hall3"), sceneTime: "13:15" }
    ),
    hall4: sovuhVnConfig(
      "19:16\n\nЭпсилон-3: Наш объект в 40 метрах от нас на запад. Постойте, 35... 30? Что за чертовщина?\n\nВ его голосе скрывался неподдельный ужас. Ситуация явно нештатная и выходит за рамки привычных вылазок на подобных миссиях.\n\nЭпсилон-3: 25... 20... 10... 5...\n\nОстальные подняли оружие и начали следить. Вы прижались к стене.\n\nЭпсилон-3: Хмм... тут стена и прохода нет. Нет, тут точно нет комнаты. Прибор, похоже, сбоит. Нужно сообщить...",
      [{ label: "Продолжить", onClick: go("breach") }],
      { background: scene("scene_hall4") }
    ),
    breach: sovuhVnConfig("", [{ label: "Продолжить", onClick: go("monster") }], { darkScene: true }),
    monster: sovuhVnConfig(
      "Когда прозвучал грохот, от неожиданности вы упали назад, поэтому не смогли запечатлеть всю сцену сразу. Из левой стены торчала какая-то рука, покрытая перьями.\n\nДва других сотрудника уже снимали с предохранителя оружие и готовились открыть огонь. Окинув взглядом окружение, вы поняли, что монстр только что пробил стену справа и протаранил третьего сотрудника, того, что был с прибором. Всё произошло в мгновение. Благодаря резкому всплеску адреналина вы смогли вскочить на ноги. Какое следующее действие?",
      [
        { label: "Достать пистолет и открыть огонь", onClick: go("shoot") },
        { label: "Бежать", onClick: go("run") }
      ],
      { background: scene("scene_monster"), sceneTime: "13:18" }
    ),
    shoot: sovuhVnConfig(
      "Вы с двумя другими сотрудниками принялись поливать свинцом чудище.\n\nКогда головы секунду назад живых коллег на большой скорости влетели в стену, вы осознали, что всё тщетно.",
      [{ label: "Продолжить", onClick: go("shootDeath") }],
      { background: scene("scene_monster") }
    ),
    shootDeath: sovuhVnConfig(
      "Смерть была быстрой, но даже эти мгновения были крайне болезненны.",
      [{ label: "Завершить", onClick: lethal("shoot") }],
      { darkScene: true }
    ),
    run: sovuhVnConfig(
      "Быстрая оценка и богатый опыт работы с аномалиями позволили понять — биться в лоб с ЭТИМ бессмысленно. Его физическая сила, судя по столь легко пробитым стенам, куда выше ожидаемого. Это точно не HE, скорее WAW или, может, даже ALEPH.\n\nВы предупредили других, что нужно бежать, но из-за паники они начали палить в сторону дыры, из которой торчала конечность аномалии. Поняв, что дальше смысла ждать нет, вы ринулись бежать.",
      [{ label: "Бежать", onClick: go("runDark") }],
      { background: scene("scene_monster") }
    ),
    runDark: sovuhVnConfig(
      "Вы бежали, не разбирая дороги. Позади звучали звуки выстрелов, но всё быстро стихло. Кажется, никто из них не выжил.",
      [{ label: "Продолжить", onClick: go("room") }],
      { darkScene: true }
    ),
    door: sovuhVnConfig(
      "Решив не терять время, вы открыли дверь, чтобы впустить товарища. Как только вы потянулись к ручке и слегка открыли дверь, холодок пробежал по спине. Владелец голоса точно был с прибором — и им пробили стену. Он не смог бы выжить, не говоря уже о том, чтобы так быстро добраться до вас.",
      [{ label: "Открыть дверь", onClick: go("doorOpen") }],
      { background: scene("scene_door") }
    ),
    doorOpen: sovuhVnConfig(
      "Дверь окончательно раскрылась, и стало ясно, что бежать некуда.\n\n???: А вот и последний.",
      [{ label: "Завершить", onClick: lethal("door") }],
      { background: scene("scene_door_open") }
    ),
    cabinet: sovuhVnConfig(
      `Это явно не его голос. Тот сотрудник не мог выжить.\n\nЭпсилон-3: Умоляю, впусти меня. Он уже близко.\n\nНе слушай его, это ловушка.\n\nЭпсилон-3: ${playerName}!\n\nВы закончили с баррикадой, ничто не пройдет внутрь.\n\n???: Да уж, заставил ты меня повозиться. Не хочешь впускать сам? Тогда не жди, что всё кончится быстро.`,
      [{ label: "Продолжить", onClick: go("cabinetDeath") }],
      { background: scene("scene_door_blocked") }
    ),
    cabinetDeath: sovuhVnConfig(
      "???: Ку-ку.\n\nЭто конец. От чудовища вас отделяют лишь остатки двери. Скоро оно прорвется...",
      [{ label: "Завершить", onClick: lethal("cabinet") }],
      { background: scene("scene_door_slammed") }
    ),
    carpet: sovuhVnConfig(
      "Вокруг ковра явно менее пыльно, чем в остальных местах, и потому вы решили проверить его. Чутьё не подвело вас — тут оказался люк!",
      [{ label: "Спуститься", onClick: go("floor4") }],
      { background: scene("scene_kovree") }
    ),
    floor4: sovuhVnConfig(
      "Вы спустились по лестнице в люке примерно на этаж ниже. Пришлось побродить, но удалось выйти в общий коридор. На стене красовалась цифра 4. Значит, 4-й этаж. Шагов не слышно — от монстра удалось оторваться.\n\nВнезапно вы услышали звук вертолёта. Похоже, он приземлился у главного входа, а не на крыше. На улице слишком темно, чтобы увидеть хоть что-то.",
      [
        { label: "Идти на звук", onClick: go("chaseText") },
        { label: "Искать путь на крышу", onClick: go("roofEscape") }
      ],
      { darkScene: true, sceneTime: "19:01" }
    ),
    chaseText: sovuhVnConfig(
      "Вы шли на источник звука, но так и не смогли разглядеть вертолёт.\n\n???: Ищешь что-то?\n\nВы обернулись на источник голоса.\n\n???: Долго же мне пришлось за тобой бегать.\n\nЭта... тварь... Это она издавала звуки...",
      [{ label: "Обернуться", onClick: go("chase") }],
      { darkScene: true }
    ),
    chase: sovuhVnConfig(
      "",
      [{ label: "Завершить", onClick: lethal("helicopter") }],
      {
        background: scene("scene_chase"),
        backgroundStyle: { objectFit: "contain", width: "50%", height: "50%", left: "25%", top: "25%" }
      }
    ),
    roofEscape: sovuhVnConfig(
      "Что-то тут нечисто. С чего бы пилот вдруг прилетел раньше? Или сел бы не там, где высадил нас?\n\nЛучше переждать на крыше.\n\nПришлось подождать полчаса, но вертолёт показался.",
      [{ label: "К вертолёту", onClick: go("final") }],
      { darkScene: true }
    ),
    final: sovuhVnConfig(
      "Когда он приземлился, вы бросились в его сторону. Дальше пусть корпорация сама разбирается. Вы поделились знаниями об этой аномалии, что помогло захватить объект и передать в комплекс.",
      [{ label: "Завершить", onClick: () => resolveSovuhZombieAction("finish").catch((error) => showRuntimeErrorModal(error)) }],
      { background: scene("scene_heli_final") }
    )
  };
  clearSovuhRoomTimer();
  if (step === "breach") {
    sovuhSound("Brick wall broke - sound effect - [High quality].mp3");
    window.setTimeout(() => sovuhSound("Screams_Shouts_human_female_002 #226679.wav"), 160);
  }
  if (step === "shoot") {
    sovuhSound("Gun Shot Sounds- MP40. ASMR..mp3");
    window.setTimeout(() => sovuhSound("Smash.wav"), 950);
  }
  if (step === "runDark") sovuhSound("Gun Shot Sounds- MP40. ASMR..mp3", 0.75);
  if (step === "chase") sovuhSound("Screams_Shouts_human_female_002 #226679.wav");
  if (step === "roomChoice") {
    const choose = (nextStep) => () => {
      clearSovuhRoomTimer();
      renderSovuhZombieScene(nextStep);
    };
    showVnChoiceModal(sovuhVnConfig("", [], {
      background: scene("scene_room"),
      sceneTime: "13:30",
      objectPrompt: `${playerName}, открой! Что делать? Осталось: 30 сек.`,
      hotspots: [
        { label: "Открыть дверь", left: "1%", top: "13%", width: "27%", height: "67%", onClick: choose("door") },
        { label: "Забаррикадировать дверь шкафом", left: "30%", top: "12%", width: "25%", height: "65%", onClick: choose("cabinet") },
        { label: "Осмотреть ковёр", left: "55%", top: "48%", width: "40%", height: "37%", onClick: choose("carpet") }
      ]
    }));
    sovuhRoomSeconds = 30;
    sovuhRoomTimer = window.setInterval(() => {
      sovuhRoomSeconds -= 1;
      if (vnObjectPrompt) vnObjectPrompt.textContent = `${playerName}, открой! Что делать? Осталось: ${Math.max(0, sovuhRoomSeconds)} сек.`;
      if (sovuhRoomSeconds <= 0) {
        clearSovuhRoomTimer();
        renderSovuhZombieScene("cabinetDeath");
      }
    }, 1000);
    return;
  }
  showVnChoiceModal(scenes[step] || scenes.intro);
}

function startSovuhZombieVn() {
  const gameMarker = activeGameSignature || "current-turn";
  const key = `sovuh-vn:${currentUserId()}:${gameMarker}:32`;
  if (window.sessionStorage.getItem(key) === "started") {
    return false;
  }
  window.sessionStorage.setItem(key, "started");
  beginSovuhVnAudio();
  renderSovuhZombieScene("intro");
  return true;
}

const PREDATOR_ANOMALY_ID = 107;
let predatorHasKnife = false;
let predatorCutThorns = false;

function predatorVnConfig(text, choices = [], options = {}) {
  return {
    nameplate: options.nameplate || 'Фильм "Predator"',
    speaker: "",
    portrait: "",
    portraitVisible: false,
    background: options.darkScene ? null : (options.background || "/photo/VN/VN_anomalyinteraction.png"),
    text,
    choices,
    hotspots: options.hotspots || [],
    objectPrompt: options.objectPrompt || "",
    darkScene: Boolean(options.darkScene),
    visualOnly: Boolean(options.visualOnly),
    input: options.input || null,
    confirmOnly: Boolean(options.confirmOnly),
    confirmLabel: options.confirmLabel || "Продолжить",
    speed: 15
  };
}

async function unlockPredatorDescription() {
  const payload = await apiPost("/api/game/predator-action", {
    user_id: currentUserId(),
    anomaly_id: PREDATOR_ANOMALY_ID,
    action: "description"
  });
  if (payload.room) renderWorkRoom(payload.room);
  showVnPopup(
    "Объект 409 — «Телевизор / Проигрыватель / Кассета».\n\n409-1 — телевизор Toshiba, 1975 год.\n409-2 — проигрыватель той же фирмы.\n409-3 — VHS-кассета с выцарапанной надписью PREDATOR.\n\nКаждые 18 часов объект необходимо приводить в действие. Через 15 минут после запуска зрителя затягивает внутрь телевизора. Дальнейшая судьба человека зависит только от него самого.\n\nОписание объекта получено."
  );
}

function showPredatorTelevisionPopup() {
  showVnPopup("На экране телевизора видны лишь помехи. Хоть он и включён, видимого источника питания не наблюдается — розетки в комнате даже нет. Возможно, аккумулятор находится внутри корпуса?");
}

function showPredatorDoorPopup() {
  showVnPopup("Вы уверены, что хотите попытаться уйти?", [
    {
      label: "Да",
      onClick: () => {
        closeVnPopup();
        playVnAudio("/sound/1.76_Defult.wav");
        predatorAction("escape").catch((error) => showRuntimeErrorModal(error));
      }
    },
    { label: "Нет", onClick: closeVnPopup }
  ]);
}

function showPredatorTapePopup() {
  showVnPopup("Вставить кассету?", [
    { label: "Да", onClick: () => startPredatorTapeTransition().catch((error) => showRuntimeErrorModal(error)) },
    {
      label: "Нет",
      onClick: () => {
        closeVnPopup();
        playVnAudio("/sound/1.76_Defult.wav");
        predatorAction("ignore").catch((error) => showRuntimeErrorModal(error));
      }
    }
  ]);
}

async function startPredatorTapeTransition() {
  closeVnPopup();
  showVnChoiceModal(predatorVnConfig("", [], {
    background: "/photo/VN/Predator/accept.png",
    visualOnly: true
  }));
  const audio = playVnAudio("/sound/240837__greenvwbeetle__creepy-sound.wav");
  await new Promise((resolve) => window.setTimeout(resolve, 900));
  showVnChoiceModal(predatorVnConfig("", [], { darkScene: true, visualOnly: true }));
  if (audio && !audio.ended && !audio.__playFailed) {
    await new Promise((resolve) => {
      const timeout = window.setTimeout(resolve, 18000);
      audio.addEventListener("ended", () => {
        window.clearTimeout(timeout);
        resolve();
      }, { once: true });
    });
  }
  renderPredatorScene("blackout1");
}

async function handlePredatorPayload(payload) {
  if (payload.room) renderWorkRoom(payload.room);
  if (payload.outcome !== "death" && !payload.player_dead) return false;
  closeVnModal();
  await showDeathModal(payload.death_narrative || payload.death_reason || "Сотрудник погиб в аномальном лесу.");
  if (showFinalResults(payload.final_results || payload.game_state?.final_results)) return true;
  if (payload.game_state?.game?.started) {
    await applyGameState(payload.game_state, { forceRefresh: true });
    return true;
  }
  closeGameScreen();
  closeOnlineScreen();
  closePlayScreen();
  return true;
}

async function predatorAction(action, nextStep = null, extra = {}) {
  if (action === "finish" && vnChoices) {
    vnChoices.querySelectorAll("button, input, textarea").forEach((element) => { element.disabled = true; });
  }
  const payload = await apiPost("/api/game/predator-action", {
    user_id: currentUserId(),
    anomaly_id: PREDATOR_ANOMALY_ID,
    action,
    ...extra
  });
  if (await handlePredatorPayload(payload)) return;
  if (payload.outcome === "completed") {
    if (payload.profanity_penalty) {
      showVnChoiceModal(predatorVnConfig(
        "Хищник прищурился: «Возможно, тебе ни к чему твой грязный язык…»\n\n…вы чувствуете, как рот наполняется кровью. (−50 HP)",
        [],
        { background: "/photo/VN/Predator/scene7.png", nameplate: "???" }
      ));
      await new Promise((resolve) => window.setTimeout(resolve, 5000));
    } else {
      if (vnChoices) vnChoices.innerHTML = "";
      await new Promise((resolve) => window.setTimeout(resolve, 5000));
    }
    await showVnChoiceModal(predatorVnConfig(
      `${payload.speech ? `«${payload.speech}» — произнесли вы.\n\n` : ""}Хмм... Похоже, что ты действительно смог протянуть. В таком случае, ты победил и можешь уходить. Приходи ещё поиграть, хи-хи.${payload.all_research_unlocked ? "\n\nВсе материалы исследования собраны." : "\n\nПодсказки открыты. Для полной награды не хватает материалов, пропущенных в предыдущих сценах."}`,
      [],
      { background: "/photo/VN/Predator/scene8.png", confirmOnly: true, confirmLabel: "Завершить", nameplate: "???" }
    ));
    return;
  }
  if (nextStep) renderPredatorScene(nextStep);
}

function renderPredatorScene(step) {
  const go = (nextStep) => () => renderPredatorScene(nextStep);
  const act = (action, nextStep, extraFactory = null) => (value = "") => predatorAction(
    action,
    nextStep,
    extraFactory ? extraFactory(value) : {}
  ).catch((error) => showRuntimeErrorModal(error));
  const scenes = {
    prelude1: predatorVnConfig(
      '"01" сентября 200* год. Корпус Эпсилон-3. Сотрудник протянул связку ключей и молча ушёл. Впереди коридора дверь. Серая, невзрачная дверь без каких-либо опознавательных знаков. Из-под двери пробивается тусклое синее свечение.',
      [],
      {
        darkScene: true,
        hotspots: [{ label: "Далее", className: "vn-dark-advance", left: "0", top: "0", width: "100%", height: "100%", onClick: go("prelude2") }]
      }
    ),
    prelude2: predatorVnConfig(
      "Снизу под дверной ручкой есть замочная скважина. Секунду вы колебались, но всё же решили воспользоваться ключами. Первый же ключ без проблем вошёл, и, прокрутив его влево, вы открыли дверь.",
      [],
      {
        darkScene: true,
        hotspots: [{ label: "Открыть дверь", className: "vn-dark-advance", left: "0", top: "0", width: "100%", height: "100%", onClick: go("intro") }]
      }
    ),
    intro: predatorVnConfig(
      "Комната выглядит убранной, хотя людей здесь явно давно не было. Информации об аномальном объекте практически нет — нужно решить, что делать.",
      [],
      {
        background: "/photo/VN/Predator/predator.png",
        objectPrompt: "Осмотрите объекты в комнате",
        hotspots: [
          { label: "Дверь", left: "0%", top: "17%", width: "31%", height: "72%", onClick: showPredatorDoorPopup },
          { label: "Телевизор", left: "39%", top: "5%", width: "32%", height: "41%", onClick: showPredatorTelevisionPopup },
          { label: "Кассета Predator", left: "40%", top: "72%", width: "25%", height: "17%", onClick: showPredatorTapePopup },
          { label: "Папка с документами", left: "68%", top: "49%", width: "30%", height: "41%", onClick: () => unlockPredatorDescription().catch((error) => showRuntimeErrorModal(error)) }
        ]
      }
    ),
    warning: predatorVnConfig(
      "Вы почувствовали слабость и тошноту. Среди помех прозвучал раздражённый голос: «ЧЕГО ТЫ ЖДЁШЬ?»",
      [
        { label: "Вставить кассету", onClick: go("forest") },
        { label: "Открыть папку", onClick: go("folder") }
      ]
    ),
    folder: predatorVnConfig(
      "Объект 409: телевизор Toshiba 1975 года, проигрыватель и VHS-кассета с надписью PREDATOR. Каждые 18 часов кассету необходимо запускать. Через 15 минут зрителя затягивает внутрь телевизора.",
      [
        { label: "Вставить кассету", onClick: go("forest") },
        { label: "Игнорировать", onClick: act("ignore") }
      ]
    ),
    blackout1: predatorVnConfig(
      "Произошло нечто странное. Вы не поняли, что именно, но оно заставило вас потерять сознание... На минуту? Час? Сложно сказать, ведь вокруг абсолютная тьма. Вы не умерли, это точно. Вы сейчас сидите на чём-то мягком и сыром.",
      [],
      {
        darkScene: true,
        hotspots: [{ label: "Далее", className: "vn-dark-advance", left: "0", top: "0", width: "100%", height: "100%", onClick: go("blackout2") }]
      }
    ),
    blackout2: predatorVnConfig(
      "Глаза по-прежнему не могут воспринимать окружение, но руки подсказывают, что это место точно не кабинет. Прохладный воздух и сырая земля под ногами говорят о том, что это улица. И явно не территория комплекса. Лес?",
      [],
      {
        darkScene: true,
        hotspots: [{ label: "Далее", className: "vn-dark-advance", left: "0", top: "0", width: "100%", height: "100%", onClick: go("blackout3") }]
      }
    ),
    blackout3: predatorVnConfig(
      "Вы бродили вперёд по ощущениям вечность, но наконец прозрели — непроглядная тьма отступила.",
      [],
      {
        darkScene: true,
        hotspots: [{ label: "Прозреть", className: "vn-dark-advance", left: "0", top: "0", width: "100%", height: "100%", onClick: go("forest") }]
      }
    ),
    forest: predatorVnConfig(
      "Перед взором предстали две тропинки. Куда идти дальше?",
      [
        { label: "Пойти влево", onClick: act("photo", "screams") },
        { label: "Пойти к дому", onClick: go("house") }
      ],
      { background: "/photo/VN/Predator/scene1.png" }
    ),
    screams: predatorVnConfig(
      "У источника криков вы увидели растерзанные тела и существо, пожирающее останки. Фото субъекта сохранено. Объект пока не обращает на вас внимания.",
      [
        { label: "Крикнуть", onClick: go("shoutAttack") },
        { label: "Стоять и смотреть", onClick: go("rules") },
        { label: "Сбежать", onClick: go("thorns") }
      ],
      { background: "/photo/VN/Predator/scene2a.png" }
    ),
    shoutAttack: predatorVnConfig(
      "Вы успешно привлекли внимание объекта. Отлично сработано! А что дальше? Ваши мысли прервал жуткий голос за спиной: «Люблю, когда моя добыча кричит, но вот когда меня отвлекают от трапезы — терпеть не могу». Вы почувствовали, как что-то тёплое стекает по спине, а затем — жгучую боль от когтей (−50 HP).",
      [{ label: "Далее", onClick: act("shout", "rules") }],
      { background: "/photo/VN/Predator/scene2a.png", nameplate: "???" }
    ),
    rules: predatorVnConfig(
      "«Позволь представиться. Я — высший хищник этого леса, и правила мои достаточно просты: доживи до первых лучей света и сможешь вернуться. Думаю, объяснять, что произойдёт, если тебе не удастся это сделать, не надо. А теперь беги...»",
      [{ label: "Сбежать", onClick: go("thorns") }],
      { background: "/photo/VN/Predator/scene2a.png", nameplate: "???" }
    ),
    house: predatorVnConfig(
      "Дом не заперт и давно заброшен. На покрытом грязью столе лежит кухонный нож. Возможно, он ещё пригодится.",
      [
        { label: "Взять нож", onClick: () => { predatorHasKnife = true; renderPredatorScene("thorns"); } },
        { label: "Не брать", onClick: go("thorns") }
      ],
      { background: "/photo/VN/Predator/scene2b.png" }
    ),
    thorns: predatorVnConfig(
      "Вы бежали со всех ног, спотыкаясь, но всеми силами стараясь удержаться на ногах. Упасть здесь означало бы смерть. Путь преградили колючки. Что делать?",
      [
        { label: "Срезать колючки", disabled: !predatorHasKnife, title: predatorHasKnife ? "" : "Нужен нож", onClick: () => { predatorCutThorns = true; renderPredatorScene("cliffIntro"); } },
        { label: "Пробиваться вперёд", onClick: () => { predatorCutThorns = false; renderPredatorScene("thornsDamage"); } }
      ],
      { background: "/photo/VN/Predator/scene3.png" }
    ),
    thornsDamage: predatorVnConfig(
      "Колючки вонзаются в плоть, но адреналин приглушает боль. Вы и сами не заметили, как пробились сквозь заросли, но всё тело кровоточит и ужасно ноет (−25 HP).",
      [{ label: "Далее", onClick: act("thorns", "cliffIntro") }],
      { background: "/photo/VN/Predator/scene3.png" }
    ),
    cliffIntro: predatorVnConfig(
      `${predatorCutThorns ? "Вы успешно прорезали себе путь и прошли дальше. Сзади раздался хохот... " : ""}Наконец вы выбрались из леса, но впереди лишь обрыв. «ХАХАХАХАХА! Вот, похоже, и конец, исследователь. Сдайся уже на мою милость».`,
      [{ label: "Далее", onClick: go("yellowEyes") }],
      { background: "/photo/VN/Predator/scene4.png", nameplate: "???" }
    ),
    yellowEyes: predatorVnConfig(
      "Жёлтые глаза — единственное, что видно из леса. Впереди пропасть, сзади кровожадный зверь. Больше путей к отступлению нет.",
      [{ label: "Далее", onClick: go("beastClose") }],
      { background: "/photo/VN/Predator/scene5.png" }
    ),
    beastClose: predatorVnConfig(
      "Зверь совсем близко. Нужно действовать.",
      [
        { label: "Броситься на зверя", onClick: go("beastDeath") },
        { label: "Атаковать ножом", disabled: !predatorHasKnife, title: predatorHasKnife ? "" : "Нужен нож", onClick: go("knifeDeath") },
        { label: "Договориться", onClick: go("lastWords") },
        { label: "Прыгнуть", onClick: go("jumpDeath") }
      ],
      { background: "/photo/VN/Predator/scene6.png" }
    ),
    beastDeath: predatorVnConfig(
      "Вы решили, что терять нечего. Когда вы приблизились и приготовились атаковать, морда кота приняла неестественное выражение. Тело оцепенело, руки перестали слушаться. Смерть неизбежна...",
      [{ label: "Принять неизбежное", onClick: act("beast") }],
      { background: "/photo/VN/Predator/scene7.png" }
    ),
    knifeDeath: predatorVnConfig(
      "С трудом взяв себя в руки, вы сделали выпад и вонзили кухонный нож в тело зверя. Вы уже приготовились праздновать, но кот резким движением вырвал нож и рванул прямо на вас. Последнее, что вы увидели, — собственное тело, пока голова ещё сохраняла остатки сознания.",
      [{ label: "...", onClick: act("knife_attack") }],
      { background: "/photo/VN/Predator/scene7.png" }
    ),
    jumpDeath: predatorVnConfig(
      "Возможно, прыжок с обрыва куда менее страшен, чем кот. Тем более остаётся надежда пережить падение. Вот только в полёте под морской поверхностью вы заметили множество острых камней...",
      [{ label: "...", onClick: act("jump") }],
      { background: "/photo/VN/Predator/scene4.png" }
    ),
    lastWords: predatorVnConfig(
      "Попробуйте договориться с хищником. Что вы ему скажете? За оскорбления он может наказать вас.",
      [{ label: "Сказать", onClick: act("finish", null, (speech) => ({ speech })) }],
      { background: "/photo/VN/Predator/scene6.png", nameplate: "???", input: { multiline: true, maxLength: 200, placeholder: "Например: «Давай договоримся…»" } }
    )
  };
  const showScene = () => {
    showVnChoiceModal(scenes[step] || scenes.intro);
    if (vnWindow) vnWindow.dataset.predatorStep = step;
  };
  const previousStep = vnWindow?.dataset.predatorStep;
  if (previousStep && previousStep !== step && !vnOverlay?.classList.contains("hidden")) {
    vnWindow.classList.remove("vn-scene-fade-in");
    vnWindow.classList.add("vn-scene-fade-out");
    window.setTimeout(() => {
      showScene();
      vnWindow.classList.remove("vn-scene-fade-out");
      void vnWindow.offsetWidth;
      vnWindow.classList.add("vn-scene-fade-in");
      window.setTimeout(() => vnWindow.classList.remove("vn-scene-fade-in"), 260);
    }, 220);
    return;
  }
  showScene();
}

function startPredatorVn() {
  const gameMarker = activeGameSignature || "current-turn";
  const key = `predator-vn:${currentUserId()}:${gameMarker}:${PREDATOR_ANOMALY_ID}`;
  if (window.sessionStorage.getItem(key) === "started") return false;
  window.sessionStorage.setItem(key, "started");
  predatorHasKnife = false;
  predatorCutThorns = false;
  if (vnWindow) delete vnWindow.dataset.predatorStep;
  renderPredatorScene("prelude1");
  return true;
}

const PUPPY_ANOMALY_ID = 66;
let puppyTouched = false;

function puppyPlayerName() {
  return discordUser?.global_name || discordUser?.username || "Сотрудник";
}

function puppyAsset(name) {
  return `/photo/VN/puppy/${name}.png`;
}

function puppyVnConfig(text, choices = [], options = {}) {
  return {
    nameplate: options.nameplate === undefined ? "" : options.nameplate,
    nameplateVisible: Boolean(options.nameplate),
    speaker: options.speaker || "",
    portraitVisible: false,
    characterVisible: true,
    background: options.background || null,
    darkScene: Boolean(options.darkScene),
    visualOnly: Boolean(options.visualOnly),
    objectPrompt: options.objectPrompt || "",
    hotspots: options.hotspots || [],
    text,
    choices,
    confirmOnly: Boolean(options.confirmOnly),
    confirmLabel: options.confirmLabel || "Продолжить",
    speed: 17
  };
}

async function puppyAction(action, nextStep = null) {
  const payload = await apiPost("/api/game/puppy-action", {
    user_id: currentUserId(),
    anomaly_id: PUPPY_ANOMALY_ID,
    action,
    touched: puppyTouched
  });
  if (payload.room) renderWorkRoom(payload.room);
  if (payload.outcome === "death" || payload.player_dead) {
    closeVnModal();
    await showDeathModal(payload.death_reason || "Сотрудник погиб после контакта со щенком.");
    if (showFinalResults(payload.final_results || payload.game_state?.final_results)) return;
    if (payload.game_state?.game?.started) {
      await applyGameState(payload.game_state, { forceRefresh: true });
      return;
    }
    closeGameScreen();
    closeOnlineScreen();
    closePlayScreen();
    return;
  }
  if (payload.outcome === "completed") {
    await showVnChoiceModal(puppyVnConfig("Похоже, что в этот раз судьба на вашей стороне.", [], {
      darkScene: true, confirmOnly: true, confirmLabel: "Завершить"
    }));
    return;
  }
  if (nextStep) renderPuppyScene(nextStep);
}

function renderPuppyScene(step) {
  const go = (nextStep) => () => renderPuppyScene(nextStep);
  const playerName = puppyPlayerName();
  const scenes = {
    intro1: puppyVnConfig("Очередная выездная миссия. Странно, что клерков, вроде тебя, привлекают к такому. Неужели в корпорации работы нет?", [{ label: "Далее", onClick: go("intro2") }], { darkScene: true }),
    intro2: puppyVnConfig("Ну да ладно, все меньше рисков умереть от какой-нибудь безумной моли или типа того.", [{ label: "Далее", onClick: go("intro3") }], { darkScene: true }),
    intro3: puppyVnConfig("Согласно вводной информации, в офисе по соседству с жилым домом слышали крики и нужно выяснить их причину.", [{ label: "Войти в офис", onClick: go("office1") }], { darkScene: true }),
    office1: puppyVnConfig("Офис хоть и выглядит как свалка, но судя по всему отсюда ушли недавно. И уходили в спешке. На некоторых столах видно кофе, который просто слегка остыл. Людей не видно, но нужно быть начеку.", [{ label: "Далее", onClick: go("office2") }], { background: puppyAsset("scene_intro") }),
    office2: puppyVnConfig("Тут вряд ли что-то интересное найдется, поэтому было решено пойти проверить конференц-зал.", [{ label: "Идти в конференц-зал", onClick: go("conference") }], { background: puppyAsset("scene_intro") }),
    conference: puppyVnConfig("", [], {
      background: puppyAsset("scene_conf"), visualOnly: true,
      objectPrompt: "Нужно найти хоть какие-то зацепки...",
      hotspots: [
        { label: "Осмотреть руку", left: "62%", top: "68%", width: "15%", height: "22%", onClick: () => showVnPopup("Под столом лежал человек. Вернее, уже труп. Его грудная клетка разорвана, но... Её как будто разорвали изнутри. Будто что-то силой пыталось освободиться и пробило путь на свободу через грудину бедняги. Смерть однозначно была болезненной.", [{ label: "Продолжить", onClick: () => { closeVnPopup(); renderPuppyScene("mystery"); } }]) },
        { label: "Продолжить поиски", left: "3%", top: "5%", width: "24%", height: "14%", onClick: go("mystery") }
      ]
    }),
    mystery: puppyVnConfig("Что за чертовщина? Здесь орудует аномалия? Но что именно могло такое сотворить?", [{ label: "Продолжить поиски", onClick: go("dog") }], { darkScene: true }),
    dog: puppyVnConfig("", [], {
      background: puppyAsset("scene_dog"), visualOnly: true,
      objectPrompt: "Блуждания по офису не дали ответов на вопросы. В одном из коридоров вы наткнулись на щенка. Что дальше?",
      hotspots: [
        { label: "Щенок", left: "41%", top: "54%", width: "17%", height: "32%", onClick: () => { puppyTouched = true; renderPuppyScene("dogTalk1"); } },
        { label: "Лестница", left: "43%", top: "19%", width: "14%", height: "34%", onClick: go("dogLeave") }
      ]
    }),
    dogTalk1: puppyVnConfig("Эй, малыш, ты чего тут делаешь?", [{ label: "Далее", onClick: go("dogTalk2") }], { background: puppyAsset("scene_dog"), nameplate: playerName }),
    dogTalk2: puppyVnConfig("*скулит*", [{ label: "Далее", onClick: go("dogTalk3") }], { background: puppyAsset("scene_dog"), nameplate: "Щенок" }),
    dogTalk3: puppyVnConfig("Не боись, мы выберемся отсюда.", [{ label: "Подняться выше", onClick: go("choiceIntro") }], { background: puppyAsset("scene_dog"), nameplate: playerName }),
    dogLeave: puppyVnConfig("Щенок не заслуживал внимания, и вы продолжили поиски.", [{ label: "Подняться выше", onClick: go("choiceIntro") }], { background: puppyAsset("scene_dog") }),
    choiceIntro: puppyVnConfig("Это последний этаж. Возможно, в кабинете директора найдутся нужные ответы. Или в комнате охраны? Сказать сложно...", [{ label: "Прислушаться", onClick: go("choiceSound") }], { background: puppyAsset("scene_choice") }),
    choiceSound: puppyVnConfig("Какого... Звук шел со стороны, куда показывает табличка с надписью «Директор».", [
      { label: "Директор", onClick: go("director1") },
      { label: "Охрана", onClick: go("securityRule") }
    ], { background: puppyAsset("scene_choice") }),
    director1: puppyVnConfig("Картина перед глазами предстала безумная: куча тел лежит в разных углах, и у всех разорвана грудная клетка. Кажется, что кричала та женщина, которая еще двигается.", [{ label: "Приблизиться", onClick: go("director2") }], { darkScene: true }),
    director2: puppyVnConfig("Вы осторожно приблизились изучить ее рану, но внутри что-то шевелилось! Оно выскочило, и от неожиданности вы упали на спину. На груди сидел тот щенок, что был этажом ниже! Вскоре он убежал, и вопросов стало еще больше.", [{ label: "Передохнуть", onClick: go("director3") }], { darkScene: true }),
    director3: puppyVnConfig("Присев отдохнуть, вы заметили кулер с водой. Выпив немного воды и приведя мысли в порядок, вы задумались о том, что видели раньше. Но странное чувство... Чувство шевеления внутри. Похоже, что оно добралось и до вас.", [{ label: "...", onClick: go("directorDeath") }], { darkScene: true }),
    directorDeath: puppyVnConfig("Последнее, что удалось увидеть, — морду щенка, который осторожно осматривал окружение из дыры в вашем теле.", [{ label: "Конец", onClick: () => puppyAction("die").catch((error) => showRuntimeErrorModal(error)) }], { darkScene: true }),
    securityRule: puppyVnConfig("Первое правило выживания в хоррорах — не идти на крики, если не готов встретиться с тем, что заставило человека кричать. А вы точно не готовы.", [{ label: "Идти к охране", onClick: go("security") }], { darkScene: true }),
    security: puppyVnConfig("", [], {
      background: puppyAsset("scene_secure"), visualOnly: true,
      objectPrompt: "Внутри комнаты охраны наверняка может быть оружие или что-то еще. И опять этот щенок — как он вообще дошел сюда?",
      hotspots: [
        { label: "Дверь охраны", left: "61%", top: "11%", width: "21%", height: "61%", onClick: go("securityDoor1") },
        { label: "Щенок", left: "75%", top: "59%", width: "17%", height: "30%", onClick: () => { puppyTouched = true; renderPuppyScene("securityPuppy1"); } }
      ]
    }),
    securityDoor1: puppyVnConfig("Щенок сам о себе может позаботиться. Тем более раз он до сих пор живой, значит твари, что творит все это, плевать на него. К счастью, дверь охраны была открыта. Заперев ее за собой, вы начали изучать окружение.", [{ label: "Осмотреть камеры", onClick: go("securityCameras") }], { darkScene: true }),
    securityPuppy1: puppyVnConfig("Ну не бросать же его в этом аду. Вы схватили щенка и потащились с ним в комнату охраны. К счастью, дверь была открыта. Заперев ее за собой, вы начали изучать окружение.", [{ label: "Осмотреть камеры", onClick: go("securityCameras") }], { darkScene: true }),
    securityCameras: puppyVnConfig("Монитор с камерами! То, что нужно. Вы начали смотреть события, происходившие в течение дня. До вашего прихода оставалось два часа — и тут появились первые жертвы.", [{ label: "Смотреть запись", onClick: go("securityTruth") }], { darkScene: true }),
    securityTruth: puppyVnConfig("...Какого хрена? Из них вылезал тот щенок! Неужели он и есть причина всего происходящего? Часть людей оставались невредимы и смогли выйти из здания, в то время как из других вылезал он. Закономерность стала очевидна: все, кто касался щенка, в итоге были мертвы.", [{ label: "Вспомнить свои действия", onClick: go("securityFinal") }], { darkScene: true }),
    securityFinal: puppyVnConfig(puppyTouched
      ? "И тут пришло осознание. А вместе с ним и паника. Вы молча посмотрели на то место, где секунду назад сидел щенок. Его нет... А внутри уже что-то шевелится..."
      : "И тут пришло осознание. А вместе с ним и паника. Вы начали судорожно вспоминать, касались ли щенка... Похоже, что в этот раз судьба на вашей стороне.", [
        { label: puppyTouched ? "Конец" : "Завершить расследование", onClick: () => puppyAction(puppyTouched ? "die" : "finish").catch((error) => showRuntimeErrorModal(error)) }
      ], { darkScene: true })
  };
  if (step === "choiceSound") {
    const first = playVnAudio("/sound/6.wav");
    let smashPlayed = false;
    const playSmash = () => {
      if (smashPlayed) return;
      smashPlayed = true;
      playVnAudio("/sound/Smash_Hit.wav");
    };
    first?.addEventListener("ended", playSmash, { once: true });
    window.setTimeout(playSmash, 1500);
  }
  if (step === "directorDeath" || (step === "securityFinal" && puppyTouched)) {
    playVnAudio("/sound/Smash_Hit.wav");
  }
  showVnChoiceModal(scenes[step] || scenes.intro1);
}

function startPuppyVn() {
  const gameMarker = activeGameSignature || "current-turn";
  const key = `puppy-vn:${currentUserId()}:${gameMarker}:${PUPPY_ANOMALY_ID}`;
  if (window.sessionStorage.getItem(key) === "started") return false;
  window.sessionStorage.setItem(key, "started");
  puppyTouched = false;
  renderPuppyScene("intro1");
  return true;
}

async function runStatChecksAnimation(effectResult) {
  const delay = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const event = effectResult?.event || {};
  const checks = Array.isArray(event.checks) ? event.checks : [];
  const unlockedHints = gameDetailsHintsList.querySelectorAll(".game-details-hint-card.unlocked");
  const lastHint = unlockedHints[unlockedHints.length - 1];
  if (!lastHint || !checks.length) return;
  const lockedButtons = [actionFinishButton, actionFleeButton, actionInventoryButton].filter(Boolean);
  const previousButtonState = lockedButtons.map((button) => ({ button, disabled: button.disabled, title: button.title }));
  lockedButtons.forEach((button) => {
    button.disabled = true;
    button.classList.add("disabled");
    button.title = "Идёт проверка характеристик.";
  });
  lastHint.querySelector(".anomaly64-stat-checks")?.remove();
  const panel = document.createElement("div");
  panel.className = "anomaly64-stat-checks";
  panel.innerHTML = checks.map((check, index) => `
    <div class="anomaly64-check" data-check-index="${index}">
      <div class="anomaly64-check-head">
        <span>${escapeHtml(check.label || `Характеристика ${index + 1}`)}</span>
        <span>Шанс ${Number(check.chance || 0)}%</span>
      </div>
      <div class="anomaly64-check-track"><div class="anomaly64-check-fill"></div></div>
      <div class="anomaly64-check-result">ПРОВЕРКА...</div>
    </div>
  `).join("");
  lastHint.appendChild(panel);
  lastHint.scrollIntoView({ behavior: "smooth", block: "nearest" });
  for (let index = 0; index < checks.length; index += 1) {
    const check = checks[index];
    const row = panel.querySelector(`[data-check-index="${index}"]`);
    const fill = row?.querySelector(".anomaly64-check-fill");
    const result = row?.querySelector(".anomaly64-check-result");
    await delay(180);
    if (fill) fill.style.width = `${Math.max(0, Math.min(100, Number(check.fill || 0)))}%`;
    await delay(1250);
    row?.classList.add(check.success ? "passed" : "failed");
    if (result) result.textContent = check.success ? "УСПЕХ" : "ПРОВАЛ — −30 SP";
    await delay(350);
  }
  applyDamageFeedback(effectResult);
  const summary = `${event.passed || 0}/4 проверок пройдено. Потеряно ${event.sp_damage || 0} SP${event.extra_hp_damage ? " и 100 HP" : ""}.`;
  await showInfoModal("Проверка характеристик", summary, {
    iconSrc: event.failed ? "/photo/work_room/badresult.png" : "/photo/work_room/success.png",
    iconAlt: "Результат проверки"
  });
  if (effectResult?.damage?.psychosis) {
    await enqueueSystemEventModal(() => showPsychosisModal(effectResult.damage.psychosis));
  }
  if (event.player_dead) {
    await showDeathModal(event.death_reason || "Не выдержал проверки характеристик");
    if (showFinalResults(event.game_state?.final_results)) return;
    if (event.game_state?.game?.started) await applyGameState(event.game_state, { forceRefresh: true });
    return;
  }
  previousButtonState.forEach(({ button, disabled, title }) => {
    button.disabled = disabled;
    button.classList.toggle("disabled", disabled);
    button.title = title;
  });
}

const TENNA_EPITHETS = ["Непревзойдённый","Обворожительный","Неподражаемый","Великолепный","Блистательный","Потрясающий","Невероятный","Удивительный","Поразительный","Феноменальный","Легендарный","Прославленный","Знаменитый","Выдающийся","Талантливый","Гениальный","Обаятельный","Харизматичный","Очаровательный","Неотразимый","Элегантный","Стильный","Эффектный","Экстравагантный","Загадочный","Таинственный","Непредсказуемый","Дерзкий","Бесстрашный","Отважный","Неукротимый","Несокрушимый","Непоколебимый","Ловкий","Хитроумный","Находчивый","Остроумный","Сообразительный","Энергичный","Неугомонный","Зажигательный","Лучезарный","Сногсшибательный","Ошеломительный","Умопомрачительный","Сенсационный","Фантастический","Невообразимый","Единственный и неповторимый"];
const TENNA_POSES = ["/photo/special/Tenna_1.png", "/photo/special/tenna2.webp", "/photo/special/tenna3.webp"];
const tennaVoice = new Audio("/sound/tenna.mp3");
const tennaApplause = new Audio("/sound/applause.mp3");

function tennaPlayVoice() { try { tennaVoice.currentTime = 0; tennaVoice.play().catch(() => {}); } catch (_) {} }
function tennaStopVoice() { try { tennaVoice.pause(); tennaVoice.currentTime = 0; } catch (_) {} }
function renderTennaPodiums(game) {
  if (!tennaPodiums) return;
  tennaPodiums.innerHTML = (game?.players || []).map((player) => `<div class="tenna-podium-avatar">${player.avatar_url ? `<img src="${escapeHtml(player.avatar_url)}" alt="${escapeHtml(player.name)}">` : `<div class="placeholder">${escapeHtml((player.name || "?").slice(0, 1).toUpperCase())}</div>`}<span>${escapeHtml(player.name)}</span></div>`).join("");
}
function setTennaPoseForNewPhrase() {
  tennaPoseIndex = (tennaPoseIndex + 1) % TENNA_POSES.length;
  if (tennaHost) tennaHost.src = TENNA_POSES[tennaPoseIndex];
}
function clearTennaTextTimers() {
  if (tennaTextTimer) window.clearInterval(tennaTextTimer);
  if (tennaAutoAdvanceTimer) window.clearTimeout(tennaAutoAdvanceTimer);
  tennaTextTimer = null; tennaAutoAdvanceTimer = null;
}
function typeTennaPhrase(text, { autoAdvance = null, hideAfter = 0 } = {}) {
  clearTennaTextTimers();
  setTennaPoseForNewPhrase();
  tennaFullText = String(text || "");
  tennaSpeech.textContent = "";
  tennaSpeech.classList.remove("hidden");
  tennaTyping = true;
  tennaPlayVoice();
  let index = 0;
  const finishTyping = () => {
    if (!tennaTyping) return;
    tennaTyping = false;
    if (tennaTextTimer) window.clearInterval(tennaTextTimer);
    tennaTextTimer = null;
    tennaSpeech.textContent = tennaFullText;
    tennaStopVoice();
    if (typeof autoAdvance === "function") tennaAutoAdvanceTimer = window.setTimeout(autoAdvance, 1000);
    else if (hideAfter > 0) tennaAutoAdvanceTimer = window.setTimeout(() => tennaSpeech.classList.add("hidden"), hideAfter);
  };
  tennaTextTimer = window.setInterval(() => {
    index = Math.min(tennaFullText.length, index + 1);
    tennaSpeech.textContent = tennaFullText.slice(0, index);
    if (index >= tennaFullText.length) finishTyping();
  }, 42);
  return finishTyping;
}
function buildTennaIntro(game) {
  const shuffled = [...TENNA_EPITHETS].sort(() => Math.random() - .5);
  return [
    { text: "ДОБРО ПОЖАЛОВАТЬ НА НАШЕ ШОУ!" },
    { text: "ПОПРИВЕТСТВУЕМ УЧАСТНИКОВ" },
    ...(game.players || []).map((player, index) => ({ text: `${shuffled[index % shuffled.length]} ${player.name}!`, applause: true })),
    { text: "НАШИ ЗРИТЕЛИ УЖЕ ЗНАЮТ ПРАВИЛА, НО ДЛЯ НАШИХ НОВЫХ УЧАСТНИКОВ Я НАПОМНЮ\n\nУ ВАС ЕСТЬ КАТЕГОРИИ С РАЗЛИЧНЫМИ ВОПРОСАМИ, ЧЕМ СЛОЖНЕЕ ВОПРОС — ТЕМ БОЛЬШЕ ОЧКОВ ОН СТОИТ. ЗА ПРАВИЛЬНЫЙ ОТВЕТ ВЫ ПОЛУЧАЕТЕ ОЧКИ, А ЗА НЕПРАВИЛЬНЫЙ ТЕРЯЕТЕ (В МИНУС ТОЖЕ МОЖНО УЙТИ)" },
    { text: "ПО ИТОГАМ ИГРЫ, ТОТ КТО НАБЕРЕТ МЕНЬШЕ ВСЕХ ОЧКОВ ОСТАНЕТСЯ ЗДЕСЬ НАВСЕГДА!\n\nИТАК, НАЧНЕМ ЖЕ ИГРУ!" }
  ];
}
function showTennaIntroLine() {
  const line = tennaIntroLines[tennaIntroIndex];
  if (!line) return;
  tennaNext.classList.remove("hidden");
  typeTennaPhrase(line.text, { autoAdvance: () => advanceTennaIntro().catch(showRuntimeErrorModal) });
  if (line.applause) { try { tennaApplause.currentTime = 0; tennaApplause.play().catch(() => {}); } catch (_) {} }
}
async function advanceTennaIntro() {
  clearTennaTextTimers();
  tennaStopVoice();
  tennaIntroIndex += 1;
  if (tennaIntroIndex < tennaIntroLines.length) { showTennaIntroLine(); return; }
  tennaSpeech.classList.add("hidden"); tennaNext.classList.add("hidden");
  if (sameUserId(activeTennaGame?.owner_id, currentUserId())) {
    const payload = await apiPost("/api/game/tenna-intro-complete", { user_id: currentUserId() });
    renderTennaGame(payload.tenna_game, true);
  } else {
    tennaCollapsed = true;
    tennaExpandedManually = false;
    tennaStageVisible = true;
    renderTennaGame(activeTennaGame);
  }
}
function tennaScoreMarkup(game) {
  return `<div class="tenna-scorebar">${(game.players || []).map((p) => `<div class="tenna-score ${sameUserId(p.id, game.current_player_id) ? "current" : ""}">${escapeHtml(p.name)}: ${Number(game.scores?.[String(p.id)] || 0)}</div>`).join("")}</div>`;
}
function startTennaDeadlineClock(game) {
  if (tennaDeadlineTimer) window.clearInterval(tennaDeadlineTimer);
  const update = () => {
    const timer = document.getElementById("tennaDecisionTimer");
    if (!timer) return;
    timer.textContent = String(Math.max(0, Math.ceil(Number(game.deadline_at || 0) - Date.now() / 1000)));
  };
  update();
  tennaDeadlineTimer = window.setInterval(update, 250);
}
function renderTennaBoard(game) {
  if (game.phase === "finished") {
    const ranking = [...(game.players || [])].sort((a, b) => Number(game.scores?.[String(b.id)] || 0) - Number(game.scores?.[String(a.id)] || 0));
    tennaBoard.innerHTML = `${tennaScoreMarkup(game)}<div class="tenna-finish"><h2>ИГРА ОКОНЧЕНА!</h2>${ranking.map((p, index) => `<div>${index + 1}. ${escapeHtml(p.name)} — ${Number(game.scores?.[String(p.id)] || 0)} очков</div>`).join("")}<button type="button" id="tennaFinishButton">ЗАВЕРШИТЬ ШОУ</button></div>`;
    tennaBoard.querySelector("#tennaFinishButton")?.addEventListener("click", async () => {
      try {
        const payload = await apiPost("/api/game/tenna-close", { user_id: currentUserId() });
        activeTennaGame = payload.tenna_game;
        tennaStageVisible = false; tennaExpandedManually = false; tennaCollapsed = false;
        tennaOverlay.classList.add("hidden"); tennaMini.classList.add("hidden");
      } catch (error) { showRuntimeErrorModal(error); }
    });
    return;
  }
  const used = new Set(game.used || []);
  const canPick = !!game.is_current_player && game.phase === "board";
  const cats = ["ZAYIN","TETH","HE","WAW","ALEPH"], points = [100,300,500,700];
  tennaBoard.innerHTML = `${tennaScoreMarkup(game)}<div class="tenna-decision-timer">ВЫБОР: <span id="tennaDecisionTimer">30</span></div><div class="tenna-grid">${cats.map(cat => `<div class="tenna-cell category">${cat}</div>${points.map(p => `<button type="button" class="tenna-cell" data-tenna-cat="${cat}" data-tenna-points="${p}" ${!canPick || used.has(`${cat}:${p}`) ? "disabled" : ""}>${used.has(`${cat}:${p}`) ? "—" : p}</button>`).join("")}`).join("")}</div>`;
  startTennaDeadlineClock(game);
  tennaBoard.querySelectorAll("[data-tenna-cat]").forEach(button => button.addEventListener("click", async () => {
    try { const payload = await apiPost("/api/game/tenna-pick", { user_id: currentUserId(), category: button.dataset.tennaCat, points: Number(button.dataset.tennaPoints) }); renderTennaGame(payload.tenna_game, true); } catch (error) { showRuntimeErrorModal(error); }
  }));
}
function renderTennaQuestion(game) {
  const q = game.question;
  if (!q) { tennaRenderedQuestionSignature = ""; tennaQuestion.classList.add("hidden"); return; }
  const signature = `${game.session_id}:${game.phase}:${game.turns_done}:${q.category}:${q.points}:${q.kind}:${game.viewer_answered ? 1 : 0}`;
  if (signature === tennaRenderedQuestionSignature) return;
  tennaRenderedQuestionSignature = signature;
  const canAnswer = game.phase === "group_question" ? !game.viewer_answered : !!game.is_current_player;
  const image = q.image ? `<img class="tenna-question-image" src="${escapeHtml(q.image)}" alt="Вопрос">` : "";
  let controls = "";
  if (q.kind === "choice") controls = `<div class="tenna-answer-list">${(q.options || []).map(option => `<button type="button" data-tenna-answer="${escapeHtml(option)}" ${canAnswer ? "" : "disabled"}>${escapeHtml(option)}</button>`).join("")}</div>`;
  else if (q.kind === "instant") controls = `<div class="tenna-answer-list"><button type="button" data-tenna-answer="" ${canAnswer ? "" : "disabled"}>ПРОДОЛЖИТЬ</button></div>`;
  else controls = `<form class="tenna-answer-form"><input name="answer" ${q.kind === "group_number" ? 'type="number"' : 'type="text"'} ${canAnswer ? "" : "disabled"} required><button type="submit" ${canAnswer ? "" : "disabled"}>ОТВЕТИТЬ</button></form>`;
  const questionTitle = q.kind === "instant" ? "АНОМАЛИЯ В МЕШКЕ" : `${escapeHtml(q.category)} — ${q.points}`;
  const questionPrompt = q.kind === "instant" && q.prompt === "Аномалия в мешке" ? "" : `<p>${escapeHtml(q.prompt)}</p>`;
  tennaQuestion.innerHTML = `${tennaScoreMarkup(game)}<div class="tenna-decision-timer">ОТВЕТ: <span id="tennaDecisionTimer">15</span></div><h2>${questionTitle}</h2>${image}${questionPrompt}${controls}${game.viewer_answered ? "<p>Ответ принят. Ждём остальных участников.</p>" : ""}`;
  startTennaDeadlineClock(game);
  tennaQuestion.querySelectorAll("[data-tenna-answer]").forEach(button => button.addEventListener("click", () => submitTennaAnswer(button.dataset.tennaAnswer)));
  tennaQuestion.querySelector("form")?.addEventListener("submit", event => { event.preventDefault(); submitTennaAnswer(new FormData(event.currentTarget).get("answer")); });
}
async function submitTennaAnswer(answer) {
  try { const payload = await apiPost("/api/game/tenna-answer", { user_id: currentUserId(), answer }); renderTennaGame(payload.tenna_game, true); } catch (error) { showRuntimeErrorModal(error); }
}
function showTennaFinalLine() {
  const line = tennaFinalLines[tennaFinalIndex];
  if (!line) {
    tennaFinalRunning = false;
    tennaSpeech.classList.add("hidden");
    if (activeTennaGame) {
      renderTennaBoard(activeTennaGame);
      if (!tennaCollapsed) tennaBoard.classList.remove("hidden");
    }
    return;
  }
  typeTennaPhrase(line.text, { autoAdvance: () => { tennaFinalIndex += 1; showTennaFinalLine(); } });
  if (line.applause) { try { tennaApplause.currentTime = 0; tennaApplause.play().catch(() => {}); } catch (_) {} }
}
function startTennaFinalNarration(game) {
  const result = game.final_result || {};
  tennaFinalSession = game.session_id;
  tennaFinalRunning = true;
  tennaFinalIndex = 0;
  tennaFinalLines = [{ text: `Итак, по итогам игры победителем стал — ${result.winner_name || "наш участник"}! Поаплодируем же нашему победителю!`, applause: true }];
  if (Number(result.player_count || 0) > 1) {
    tennaFinalLines.push({ text: "Остальные же тоже не уйдут без подарков, ведь начисленные очки будут выданы игрокам как СО." });
    if (result.eliminated_name) tennaFinalLines.push({ text: `А вот ${result.eliminated_name} — попрошу остаться.` });
  } else {
    tennaFinalLines.push({ text: "Сегодня был всего один игрок, но его желание блистать на сцене было просто неповторимо! Пожелаем же удачи ему в дальнейших работах!" });
  }
  tennaBoard.classList.add("hidden"); tennaQuestion.classList.add("hidden");
  showTennaFinalLine();
}
function renderTennaGame(game, forceOpen = false) {
  activeTennaGame = game;
  if (!game?.active) { tennaOverlay?.classList.add("hidden"); tennaMini?.classList.add("hidden"); return; }
  renderTennaPodiums(game);
  if (game.phase === "intro" && tennaIntroSession !== String(game.session_id || "")) {
    tennaIntroSession = String(game.session_id || "");
    tennaIntroLines = buildTennaIntro(game); tennaIntroIndex = 0; forceOpen = true; showTennaIntroLine();
  }
  if (forceOpen || tennaExpandedManually || game.is_current_player || sameUserId(game.owner_id, currentUserId()) && game.phase === "intro") tennaStageVisible = true;
  const shouldShowStage = tennaStageVisible;
  const shouldExpandPanel = shouldShowStage && !tennaCollapsed;
  tennaOverlay.classList.toggle("hidden", !shouldShowStage);
  tennaMini.classList.toggle("hidden", shouldExpandPanel);
  tennaCollapse.classList.toggle("hidden", game.phase === "intro");
  tennaBoard.classList.toggle("hidden", !shouldExpandPanel || game.phase !== "board" && game.phase !== "finished" || game.phase === "finished" && tennaFinalRunning);
  tennaQuestion.classList.toggle("hidden", !shouldExpandPanel || !["question","group_question"].includes(game.phase));
  if (game.phase === "board") { tennaRenderedQuestionSignature = ""; renderTennaBoard(game); }
  if (game.phase === "finished" && game.session_id !== tennaFinalSession) startTennaFinalNarration(game);
  else if (game.phase === "finished" && !tennaFinalRunning) renderTennaBoard(game);
  if (["question","group_question"].includes(game.phase)) renderTennaQuestion(game);
  const reactionSignature = game.reaction ? `${game.turns_done}:${game.reaction.text}:${game.reaction.detail || ""}` : "";
  if (game.phase !== "finished" && game.reaction && reactionSignature !== tennaReactionSignature) {
    tennaReactionSignature = reactionSignature;
    typeTennaPhrase(`${game.reaction.text}\n${game.reaction.detail || ""}`, { hideAfter: 1800 });
    if (game.reaction.applause) { try { tennaApplause.currentTime = 0; tennaApplause.play().catch(() => {}); } catch (_) {} }
  }
  const current = (game.players || []).find(p => sameUserId(p.id, game.current_player_id));
  tennaMiniText.textContent = game.phase === "finished" ? "ИГРА ОКОНЧЕНА — РАЗВЕРНУТЬ" : `ХОД: ${current?.name || "участник"} — РАЗВЕРНУТЬ`;
}
async function startTennaShow(anomalyId = 104) {
  const payload = await apiPost("/api/game/tenna-start", { user_id: currentUserId(), anomaly_id: anomalyId });
  tennaCollapsed = false; tennaExpandedManually = true; tennaStageVisible = true; renderTennaGame(payload.tenna_game, true);
}
tennaNext?.addEventListener("click", () => {
  if (tennaTyping) {
    clearTennaTextTimers(); tennaTyping = false; tennaSpeech.textContent = tennaFullText; tennaStopVoice();
    tennaAutoAdvanceTimer = window.setTimeout(() => advanceTennaIntro().catch(showRuntimeErrorModal), 1000);
    return;
  }
  advanceTennaIntro().catch(showRuntimeErrorModal);
});
tennaCollapse?.addEventListener("click", () => { tennaCollapsed = true; tennaExpandedManually = false; tennaStageVisible = true; renderTennaGame(activeTennaGame); });
tennaMini?.addEventListener("click", () => { tennaCollapsed = false; tennaExpandedManually = true; tennaStageVisible = true; renderTennaGame(activeTennaGame, true); });

async function openInstrumentChoice(anomalyId = 106) {
  const preview = await apiPost("/api/game/instrument-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  if (!preview.pending) {
    await showDetailsInfoModal({
      intro: "Инструмент уже выбран",
      effect: "Повторно изменить выбор нельзя.",
      icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
      iconAlt: "Выбор инструмента"
    });
    return;
  }
  showDetailsChoiceModal({
    intro: preview.intro,
    effect: preview.effect,
    icon: activeRoomPayload?.model_url || "/photo/work_room/hinthidden.png",
    iconAlt: "Музыкальные инструменты",
    choices: (preview.choices || []).map((choice) => ({
      label: choice.label,
      title: choice.description,
      onClick: async () => {
        try {
          const payload = await apiPost("/api/game/instrument-choose", {
            user_id: currentUserId(), anomaly_id: anomalyId, choice: choice.key
          });
          closeDetailsEventModal();
          if (payload.room) renderWorkRoom(payload.room);
          await showDetailsInfoModal({
            intro: "Выбор сделан",
            effect: payload.message,
            icon: activeRoomPayload?.model_url || "/photo/work_room/success.png",
            iconAlt: choice.label
          });
        } catch (error) { showRuntimeErrorModal(error); }
      }
    }))
  });
}

async function openPandoraBox(anomalyId = 113) {
  const preview = await apiPost("/api/game/pandora-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  showDetailsChoiceModal({
    intro: preview.intro || "Ящик Пандоры",
    effect: preview.effect || "Выберите один предмет:",
    icon: activeRoomPayload?.model_url || "/photo/work_room/hinthidden.png",
    iconAlt: "Ящик Пандоры",
    choices: (preview.choices || []).map((choice) => ({
      label: choice.name || choice.label,
      onClick: async () => {
        try {
          const payload = await apiPost("/api/game/pandora-choose", {
            user_id: currentUserId(),
            anomaly_id: anomalyId,
            item_id: choice.item_id
          });
          closeDetailsEventModal();
          if (payload.room) renderWorkRoom(payload.room);
          await showDetailsInfoModal({
            intro: payload.ok ? "Предмет получен" : "Предмет не выдан",
            effect: payload.message,
            icon: payload.ok ? "/photo/work_room/giveitem.png" : "/photo/work_room/badresult.png",
            iconAlt: payload.ok ? "Предмет получен" : "Инвентарь переполнен"
          });
        } catch (error) {
          await showRuntimeErrorModal(error);
        }
      }
    }))
  });
}

function renderPortal116Dialog(portal, anomalyId = 116) {
  if (!portal?.pending) {
    showDetailsInfoModal({
      intro: portal?.intro || "Лесной портал",
      effect: portal?.effect || "Больше ничего необычного тут нет.",
      icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
      iconAlt: "Лесной портал"
    });
    return;
  }
  showDetailsChoiceModal({
    intro: portal.intro || "Лесной портал",
    effect: portal.effect || "",
    icon: activeRoomPayload?.model_url || "/photo/work_room/hinthidden.png",
    iconAlt: "Лесной портал",
    choices: (portal.choices || []).map((choice) => ({
      label: choice.label,
      onClick: async () => {
        try {
          const payload = await apiPost("/api/game/portal116-action", {
            user_id: currentUserId(),
            anomaly_id: anomalyId,
            action: choice.key
          });
          if (!payload.resolved) {
            renderPortal116Dialog(payload.portal, anomalyId);
            return;
          }
          closeDetailsEventModal();
          if (payload.room) renderWorkRoom(payload.room);
          await showDetailsInfoModal({
            intro: "Лесной портал",
            effect: payload.message || "Больше ничего необычного тут нет.",
            icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
            iconAlt: "Лесной портал"
          });
        } catch (error) {
          await showRuntimeErrorModal(error);
        }
      }
    }))
  });
}

async function openPortal116(anomalyId = 116) {
  const portal = await apiPost("/api/game/portal116-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  renderPortal116Dialog(portal, anomalyId);
}

async function openGlobalRift135(anomalyId = 135) {
  const preview = await apiPost("/api/game/rift135-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  const choices = Array.isArray(preview?.choices) ? preview.choices : [];
  const mode = preview?.mode === "swap" ? "swap" : "deposit";
  const emptyText = mode === "swap"
    ? "У вас нет предмета, который можно оставить взамен."
    : "У вас нет предмета, который можно положить в разлом.";
  showDetailsChoiceModal({
    intro: preview?.intro || "Межпространственный разлом",
    effect: `${preview?.effect || ""}${choices.length ? "" : `\n\n${emptyText}`}`,
    icon: activeRoomPayload?.model_url || "/photo/work_room/hinthidden.png",
    iconAlt: "Межпространственный разлом",
    choices: [
      ...choices.map((item) => ({
        label: item.label || item.name,
        onClick: async () => {
          try {
            const payload = await apiPost("/api/game/rift135-action", {
              user_id: currentUserId(),
              anomaly_id: anomalyId,
              action: mode,
              slot: item.slot
            });
            closeDetailsEventModal();
            if (payload.room) renderWorkRoom(payload.room);
            await showDetailsInfoModal({
              intro: mode === "swap" ? "Обмен завершён" : "Предмет помещён",
              effect: payload.message,
              icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
              iconAlt: "Межпространственный разлом"
            });
          } catch (error) {
            await showRuntimeErrorModal(error);
          }
        }
      })),
      { label: "Отмена", onClick: async () => closeDetailsEventModal() }
    ]
  });
}

async function openDice120Choice(anomalyId = 120) {
  const preview = await apiPost("/api/game/dice120-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  if (!preview.pending) {
    await showDetailsInfoModal({
      intro: preview.intro || "Набор игральных кубиков",
      effect: preview.effect || "Кубик уже выбран.",
      icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
      iconAlt: "Игральные кубики"
    });
    return;
  }
  showDetailsChoiceModal({
    intro: preview.intro || "Набор игральных кубиков",
    effect: preview.effect || "Выберите один кубик:",
    icon: activeRoomPayload?.model_url || "/photo/work_room/hinthidden.png",
    iconAlt: "Игральные кубики",
    choices: (preview.choices || []).map((choice) => ({
      label: choice.label,
      onClick: async () => {
        try {
          const payload = await apiPost("/api/game/dice120-choose", {
            user_id: currentUserId(),
            anomaly_id: anomalyId,
            choice: choice.key
          });
          closeDetailsEventModal();
          if (payload.room) renderWorkRoom(payload.room);
          await showDetailsInfoModal({
            intro: payload.ok ? "Кубик получен" : "Кубик не выдан",
            effect: payload.message,
            icon: payload.ok ? "/photo/work_room/giveitem.png" : "/photo/work_room/badresult.png",
            iconAlt: choice.label
          });
        } catch (error) {
          await showRuntimeErrorModal(error);
        }
      }
    }))
  });
}

async function openPet122Choice(anomalyId = 122) {
  const preview = await apiPost("/api/game/pet122-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  if (!preview.pending) {
    await showDetailsInfoModal({
      intro: preview.intro || "Кот Вельмондт",
      effect: preview.effect || "Взаимодействие уже завершено.",
      icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
      iconAlt: "Кот Вельмондт"
    });
    return;
  }
  showDetailsChoiceModal({
    intro: preview.intro || "Кот Вельмондт",
    effect: preview.effect || "Погладить аномалию?",
    icon: activeRoomPayload?.model_url || "/photo/work_room/hinthidden.png",
    iconAlt: "Кот Вельмондт",
    choices: (preview.choices || []).map((choice) => ({
      label: choice.label,
      onClick: async () => {
        try {
          const payload = await apiPost("/api/game/pet122-action", {
            user_id: currentUserId(),
            anomaly_id: anomalyId,
            action: choice.key
          });
          closeDetailsEventModal();
          if (payload.room) renderWorkRoom(payload.room);
          await showDetailsInfoModal({
            intro: "Кот Вельмондт",
            effect: payload.message,
            icon: activeRoomPayload?.model_url || "/photo/work_room/neutralresult.png",
            iconAlt: "Кот Вельмондт"
          });
        } catch (error) {
          await showRuntimeErrorModal(error);
        }
      }
    }))
  });
}

async function openGish125Feed(anomalyId = 125) {
  const preview=await apiPost("/api/game/gish125-preview",{user_id:currentUserId(),anomaly_id:anomalyId});
  if(!preview.pending){
    await showDetailsInfoModal({
      intro:preview.intro||"Покормить Гиша",
      effect:preview.effect||"У вас нет подходящих предметов.",
      icon:activeRoomPayload?.model_url||"/photo/work_room/neutralresult.png",
      iconAlt:"Гиш"
    });
    return;
  }
  showDetailsChoiceModal({
    intro:preview.intro||"Покормить Гиша",
    effect:preview.effect||"Выберите предмет, который Гиш съест.",
    icon:activeRoomPayload?.model_url||"/photo/work_room/hinthidden.png",
    iconAlt:"Гиш",
    choices:[
      ...(preview.choices||[]).map(item=>({
        label:item.label||item.name,
        onClick:async()=>{
          try{
            const payload=await apiPost("/api/game/gish125-feed",{user_id:currentUserId(),anomaly_id:anomalyId,slot:item.slot});
            closeDetailsEventModal();
            if(payload.room)renderWorkRoom(payload.room);
            await showDetailsInfoModal({intro:"Гиш поел",effect:payload.message,icon:activeRoomPayload?.model_url||"/photo/work_room/neutralresult.png",iconAlt:"Гиш"});
          }catch(error){await showRuntimeErrorModal(error);}
        }
      })),
      {label:"Не кормить",onClick:async()=>closeDetailsEventModal()}
    ]
  });
}

let activePo3Event = null;
let po3RenderedSignature = "";
let po3TimerInterval = null;
function ensurePo3Overlay() {
  let overlay = document.getElementById("po3EventOverlay");
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.id = "po3EventOverlay";
  overlay.className = "po3-event-overlay hidden";
  overlay.innerHTML = `<div class="po3-event-stage"><img class="po3-event-image hidden" alt="PO-3"><div class="po3-event-title"></div><div class="po3-event-text"></div><div class="po3-event-timer hidden"></div><div class="po3-event-actions"></div></div>`;
  document.body.appendChild(overlay);
  return overlay;
}
async function refreshPo3Event() {
  const payload = await apiPost("/api/game/po3-state", { user_id: currentUserId() });
  renderPo3Event(payload.po3_event, true);
}
function po3Buttons(overlay, buttons) {
  const wrap = overlay.querySelector(".po3-event-actions");
  wrap.innerHTML = "";
  buttons.forEach(({label, action, disabled=false, cls=""}) => {
    const button = document.createElement("button"); button.type="button"; button.textContent=label; button.className=cls; button.disabled=disabled;
    button.addEventListener("click", action); wrap.appendChild(button);
  });
}
function renderPo3WireOrder(overlay, event, challenge) {
  const wrap = overlay.querySelector(".po3-event-actions");
  wrap.innerHTML = "";
  const list = document.createElement("div");
  list.className = "po3-wire-order";
  const colors = {
    "Оранжевый":"#ff8a00", "Красный":"#e63737", "Жёлтый":"#ffe43b", "Синий":"#3185ff",
    "Белый":"#f4f4f4", "Чёрный":"#171717", "Зелёный":"#32bf59", "Пурпурный":"#a74cdb"
  };
  let dragged = null;
  (challenge.options || []).forEach((color, index) => {
    const row = document.createElement("div");
    row.className = "po3-wire-slot";
    row.draggable = true;
    row.dataset.color = String(color);
    row.innerHTML = `<span class="po3-wire-position">${index + 1}</span><span class="po3-wire-swatch"></span><span>${String(color)}</span>`;
    row.querySelector(".po3-wire-swatch").style.background = colors[color] || "#777";
    row.addEventListener("dragstart", () => { dragged = row; row.classList.add("dragging"); });
    row.addEventListener("dragend", () => { row.classList.remove("dragging"); dragged = null; refreshPositions(); });
    row.addEventListener("dragover", (ev) => {
      ev.preventDefault();
      if (!dragged || dragged === row) return;
      const rect = row.getBoundingClientRect();
      list.insertBefore(dragged, ev.clientY < rect.top + rect.height / 2 ? row : row.nextSibling);
    });
    list.appendChild(row);
  });
  const refreshPositions = () => [...list.children].forEach((row, index) => { row.querySelector(".po3-wire-position").textContent = String(index + 1); });
  const confirm = document.createElement("button");
  confirm.type = "button";
  confirm.textContent = "Подтвердить";
  confirm.addEventListener("click", async () => {
    confirm.disabled = true;
    try {
      const order = [...list.querySelectorAll(".po3-wire-slot")].map(row => row.dataset.color);
      const payload = await apiPost("/api/game/po3-answer", {user_id:currentUserId(), answer:JSON.stringify(order), revision:event.revision});
      renderPo3Event(payload.po3_event, true);
    } catch (error) {
      confirm.disabled = false;
      showRuntimeErrorModal(error);
    }
  });
  wrap.append(list, confirm);
}
function po3Deadline(overlay, deadline) {
  const timer=overlay.querySelector(".po3-event-timer");
  if(po3TimerInterval){window.clearInterval(po3TimerInterval);po3TimerInterval=null;}
  if(!deadline){timer.classList.add("hidden");return;}
  timer.classList.remove("hidden");
  const update=()=>{timer.textContent=`ОСТАЛОСЬ: ${Math.max(0,Math.ceil(Number(deadline)-Date.now()/1000))}`;}; update();
  po3TimerInterval=window.setInterval(update,250);
  window.setTimeout(()=>refreshPo3Event().catch(()=>{}),Math.max(100,Number(deadline)*1000-Date.now()+150));
}
function renderPo3Event(event, force=false) {
  const overlay=ensurePo3Overlay();
  if(!event?.active){overlay.classList.add("hidden");activePo3Event=null;return;}
  const finishedStorageKey=`po3-finished:${event.session_id}`;
  if(event.phase==="finished"&&window.localStorage.getItem(finishedStorageKey)==="1"){
    overlay.classList.add("hidden");activePo3Event=null;return;
  }
  activePo3Event=event;
  const signature=`${event.session_id}:${event.revision}:${event.phase}:${event.is_current_player}`;
  if(!force&&signature===po3RenderedSignature)return;
  po3RenderedSignature=signature; overlay.classList.remove("hidden");
  const image=overlay.querySelector(".po3-event-image"),title=overlay.querySelector(".po3-event-title"),text=overlay.querySelector(".po3-event-text");
  image.classList.add("hidden"); title.className="po3-event-title"; title.textContent=""; text.textContent=""; po3Deadline(overlay,event.deadline);
  if(event.phase==="access"){
    title.classList.add("access"); title.textContent="Дать доступ к локальным файлам?";
    if(!event.is_owner){text.textContent="Инициатор принимает решение…";po3Buttons(overlay,[]);return;}
    po3Buttons(overlay,[
      {label:"Да",action:async()=>{const p=await apiPost("/api/game/po3-access",{user_id:currentUserId(),revision:event.revision});renderPo3Event(p.po3_event,true);}},
      {label:"Нет",cls:"po3-no-button",action:()=>{}}
    ]);
    const wrap=overlay.querySelector(".po3-event-actions"),no=wrap.querySelector(".po3-no-button");
    no?.addEventListener("mouseenter",()=>{wrap.insertBefore(no,wrap.firstElementChild===no?null:wrap.firstElementChild);});
    return;
  }
  image.src="/photo/PO3/po3_neutral.png"; image.classList.remove("hidden");
  if(event.phase==="dialog"){
    title.textContent="PO-3"; text.textContent="Приветствую. Вас ожидает небольшое испытание. Вы сами будете вольны выбирать его из списка, но знайте — ошибки недопустимы.";
    po3Buttons(overlay,event.is_owner?[{label:"Продолжить",action:async()=>{const p=await apiPost("/api/game/po3-begin",{user_id:currentUserId(),revision:event.revision});renderPo3Event(p.po3_event,true);}}]:[]);return;
  }
  if(event.phase==="finished"){
    image.src="/photo/PO3/po3_angry.png"; title.textContent="ИСПЫТАНИЯ ЗАВЕРШЕНЫ";
    text.textContent="Результаты подведены. Все доступные сведения об аномалии открыты.";
    po3Buttons(overlay,[{label:"ОК",action:async()=>{
      window.localStorage.setItem(finishedStorageKey,"1");overlay.classList.add("hidden");activePo3Event=null;
      try{await apiPost("/api/game/po3-ack",{user_id:currentUserId()});}catch(_){/* локальная защита уже скрыла повтор */}
    }}]);return;
  }
  if(event.phase==="failed_notice"){
    if(!event.is_current_player){
      image.src="/photo/PO3/po3_neutral.png"; title.textContent="PO-3";
      text.textContent="Ожидайте свой ход"; po3Deadline(overlay,null); po3Buttons(overlay,[]); return;
    }
    image.src="/photo/PO3/po3_smile.png"; title.textContent="PO-3";
    text.textContent="Ой, ой, кажется кто-то ошибся. Какая жалость";
    po3Buttons(overlay,event.is_current_player?[{label:"Продолжить",action:async()=>{const p=await apiPost("/api/game/po3-failure-continue",{user_id:currentUserId(),revision:event.revision});renderPo3Event(p.po3_event,true);}}]:[]);
    return;
  }
  if(event.phase==="results_winners"){
    image.src="/photo/PO3/po3_angry.png"; title.textContent="ИТОГИ ИСПЫТАНИЙ";
    text.textContent=`Успешно прошли испытание: ${(event.winners||[]).map(p=>p.name).join(", ")||"никто"}.`;
    po3Buttons(overlay,event.is_owner?[{label:"Далее",action:async()=>{const p=await apiPost("/api/game/po3-results-next",{user_id:currentUserId(),revision:event.revision});renderPo3Event(p.po3_event,true);}}]:[]);
    return;
  }
  if(event.phase==="results_losers"){
    image.src="/photo/PO3/po3_angry.png"; title.textContent="ИТОГИ ИСПЫТАНИЙ";
    text.textContent=`Испытание не прошли: ${(event.losers||[]).map(p=>p.name).join(", ")}. Они будут устранены.`;
    po3Buttons(overlay,event.is_owner?[{label:"Завершить",action:async()=>{const p=await apiPost("/api/game/po3-results-next",{user_id:currentUserId(),revision:event.revision});renderPo3Event(p.po3_event,true);if(p.game_state)await applyGameState(p.game_state,{forceRefresh:true});}}]:[]);
    return;
  }
  if(event.phase==="results_all_success"){
    image.src="/photo/PO3/po3_angry.png"; title.textContent="ИТОГИ ИСПЫТАНИЙ";
    text.textContent="В этот раз вам всем повезло";
    po3Buttons(overlay,event.is_owner?[{label:"Завершить",action:async()=>{const p=await apiPost("/api/game/po3-results-next",{user_id:currentUserId(),revision:event.revision});renderPo3Event(p.po3_event,true);if(p.game_state)await applyGameState(p.game_state,{forceRefresh:true});}}]:[]);
    return;
  }
  title.textContent=`СЕЙЧАС ИСПЫТАНИЕ ПРОХОДИТ: ${event.current_player_name}`;
  if(event.phase==="select"){
    text.textContent=event.is_current_player?"Выберите испытание:":"Ожидайте свой ход";
    po3Buttons(overlay,event.is_current_player?(event.available_trials||[]).map((id)=>({label:`${id} — ${["","Аномалий","Математики","Обезвреживания","Памяти"][id]}`,action:async()=>{const p=await apiPost("/api/game/po3-choose",{user_id:currentUserId(),choice:id,revision:event.revision});renderPo3Event(p.po3_event,true);}})):[]);return;
  }
  if(!event.is_current_player){
    title.textContent="PO-3"; text.textContent="Ожидайте свой ход"; po3Deadline(overlay,null); po3Buttons(overlay,[]); return;
  }
  const q=event.challenge||{};
  if(q.image){image.src=q.image;image.classList.remove("hidden");}
  if(event.phase==="memorize"){
    text.textContent=`Запоминайте символы:\n\n${q.memorize||""}`; po3Buttons(overlay,[]); return;
  }
  const rules=q.rules?`${q.rules}\n\n`:""; text.textContent=`Испытание: ${event.choice_name||""}\nРаунд ${Number(event.round||0)+1}\n\n${rules}${q.prompt||""}`;
  if(q.kind === "wire_order"){
    renderPo3WireOrder(overlay, event, q);
    return;
  }
  po3Buttons(overlay,(q.options||[]).map(option=>({
    label:String(option),
    disabled:!event.is_current_player,
    action:async()=>{
      try{
        const p=await apiPost("/api/game/po3-answer",{user_id:currentUserId(),answer:String(option),revision:event.revision});
        renderPo3Event(p.po3_event,true);
      }catch(error){showRuntimeErrorModal(error);}
    }
  })));
}
async function startPo3Event(){
  const overlay=ensurePo3Overlay(); overlay.classList.remove("hidden");
  overlay.querySelector(".po3-event-image").classList.add("hidden");
  overlay.querySelector(".po3-event-title").textContent=""; overlay.querySelector(".po3-event-text").textContent="";
  po3Buttons(overlay,[]);
  await new Promise(resolve=>window.setTimeout(resolve,1000));
  const payload=await apiPost("/api/game/po3-state",{user_id:currentUserId()});renderPo3Event(payload.po3_event,true);
}

async function handleQueuedUiEvent(effectResult, details = null) {
  const event = effectResult?.event;
  if (!event?.type) return false;
  if (event.type === "instrument_choice_dialog") {
    await openInstrumentChoice(event.anomaly_id || activeRoomAnomalyId || 106);
    return true;
  }
  if (event.type === "pandora_box_dialog") {
    await openPandoraBox(event.anomaly_id || activeRoomAnomalyId || 113);
    return true;
  }
  if (event.type === "portal_mushroom_dialog") {
    await openPortal116(event.anomaly_id || activeRoomAnomalyId || 116);
    return true;
  }
  if (event.type === "global_rift_dialog") {
    await openGlobalRift135(event.anomaly_id || activeRoomAnomalyId || 135);
    return true;
  }
  if (event.type === "dice_pick_dialog") {
    await openDice120Choice(event.anomaly_id || activeRoomAnomalyId || 120);
    return true;
  }
  if (event.type === "pet_anomaly_prompt") {
    await openPet122Choice(event.anomaly_id || activeRoomAnomalyId || 122);
    return true;
  }
  if(event.type==="feedable_anomaly_prompt"){
    await openGish125Feed(event.anomaly_id||activeRoomAnomalyId||125);
    return true;
  }
  if(event.type==="po3_trials"){
    await startPo3Event();
    return true;
  }
  if (event.type === "tenna_game") {
    await startTennaShow(event.anomaly_id || 104);
    return true;
  }
  if (event.type === "flee_effect") {
    await showDetailsInfoModal({
      intro: "Проверка не пройдена",
      effect: "Без активного сигнала от berserk17 дальнейшее исследование невозможно. Сотрудник покидает камеру содержания.",
      icon: "/photo/work_room/neutralresult.png",
      iconAlt: "Проверка не пройдена"
    });
    const payload = await apiPost("/api/game/flee", {
      user_id: currentUserId()
    });
    finishPreviewActive = false;
    lastFinishReward = { cp: 0, rt: 0 };
    closeStatUpgradeModal();
    activeRoomPayload = null;
    currentDetailsPayload = null;
    if (payload.player_dead) {
      await showDeathModal(getDeathReasonFromPayload(payload));
      if (showFinalResults(payload.game_state?.final_results)) {
        return true;
      }
    }
    if (payload.game_state?.game?.started) {
      await applyGameState(payload.game_state, { forceRefresh: true });
      return true;
    }
    if (showFinalResults(payload.game_state?.final_results)) {
      return true;
    }
    closeGameScreen();
    onlineScreen.classList.remove("hidden");
    openOnlineRoomView();
    await loadOnlineLobby();
    return true;
  }
  if (event.type === "nubert_dialog") {
    const codeName = details?.base_info?.code_name || `SC-UN-U-${event.anomaly_id || 0}`;
    await runNubertDialog(codeName);
    return true;
  }
  if (event.type === "kill_contract_offer") {
    await openKillContractOffer(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "stat_conversion_offer") {
    await openStatConversionOffer(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "death_shield_offer") {
    await openDeathShieldOffer(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "altar_offering") {
    await openAltarOffering(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "devil_deal_offer") {
    await openDevilDeal(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "free_stat_offer") {
    await openFreeStatOffer(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "curse_anomaly_dialog") {
    await openCurse137Offer(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id || 137);
    return true;
  }
  if (event.type === "anomaly51_number_input") {
    openAnomaly51NumberInput();
    return true;
  }
  if (event.type === "moon_eye_game") {
    await startMoonEyeGame(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "emoji_glasses_game") {
    await startEmojiGlassesGame(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "sea_monster_game") {
    await startSeaMonsterGame(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "stat_checks") {
    await runStatChecksAnimation(effectResult);
    return true;
  }
  if (event.type === "choose_bonus_offer") {
    openChooseBonusOffer(event.anomaly_id || activeRoomAnomalyId || details?.anomaly_id);
    return true;
  }
  if (event.type === "sovuh_zombie_game") {
    startSovuhZombieVn();
    return true;
  }
  if (event.type === "forest_tape_dialog") {
    startPredatorVn();
    return true;
  }
  if (event.type === "puppy_encounter") {
    startPuppyVn();
    return true;
  }
  await showDetailsInfoModal({
    intro: effectResult?.title || "Событие аномалии",
    effect: effectResult?.description || "Взаимодействие завершено.",
    icon: event.asset || "/photo/work_room/neutralresult.png",
    iconAlt: effectResult?.title || "Событие аномалии"
  });
  return true;
}

function showHeartAttackModal() {
  if (!eventOverlay) return Promise.resolve();
  eventIcon.src = "/photo/work_room/heartattack.png";
  eventIcon.alt = "Сердечный приступ";
  eventIntro.textContent = "Уровень рассудка достиг критического минимума. Введен анксиолитик (текущий рассудок установлен в размере 50). Побочный эффект - снижение активности сердечной мышцы (текущее здоровье равно 1). ВНИМАНИЕ: повторное применение анксиолитика при низком показателя здоровья приведет к смерти!";
  eventRollerWrap.classList.add("hidden");
  eventEffect.textContent = "";
  eventConfirmButton.classList.remove("hidden");
  eventOverlay.classList.remove("hidden");
  return new Promise((resolve) => {
    eventModalResolver = resolve;
  });
}

function showDeathModal(reasonText) {
  if (!eventOverlay) return Promise.resolve();
  deathModalActive = true;
  eventIcon.classList.remove("hidden");
  eventIcon.src = "/photo/work_room/heartattack.png";
  eventIcon.alt = "Смерть";
  eventIntro.textContent = "Вы погибли";
  eventRollerWrap.classList.add("hidden");
  eventEffect.textContent = reasonText || "Причина смерти неизвестна.";
  eventConfirmButton.classList.remove("hidden");
  eventOverlay.classList.remove("hidden");
  return new Promise((resolve) => {
    eventModalResolver = resolve;
  });
}

function showInfoModal(introText, effectText = "", options = {}) {
  if (deathModalActive) return Promise.resolve();
  if (!eventOverlay) return Promise.resolve();
  eventRollerWrap.classList.add("hidden");
  eventChoices.innerHTML = "";
  eventConfirmButton.classList.remove("hidden");
  eventIntro.textContent = introText || "";
  eventEffect.textContent = effectText || "";
  if (options.hideIcon) {
    eventIcon.classList.add("hidden");
    eventIcon.removeAttribute("src");
    eventIcon.alt = "";
  } else {
    eventIcon.classList.remove("hidden");
    eventIcon.src = options.iconSrc || activeRoomPayload?.model_url || "/photo/work_room/404.png";
    eventIcon.alt = options.iconAlt || "Событие";
  }
  eventOverlay.classList.remove("hidden");
  return new Promise((resolve) => {
    eventModalResolver = resolve;
  });
}

async function consumeIlvetalNotice(anomalyId = activeRoomAnomalyId) {
  const payload = await apiPost("/api/game/consume-ilvetal-notice", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  if (payload.room) {
    renderWorkRoom(payload.room);
  } else if (activeRoomPayload?.ilvetal_notice) {
    activeRoomPayload.ilvetal_notice = { pending: false };
  }
  return payload;
}

async function consumeCheapTrickNotice(anomalyId = activeRoomAnomalyId) {
  const payload = await apiPost("/api/game/consume-cheaptrick-notice", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  if (payload.room) {
    renderWorkRoom(payload.room);
  } else if (activeRoomPayload?.cheaptrick_notice) {
    activeRoomPayload.cheaptrick_notice = { pending: false };
  }
  return payload;
}

async function showIlvetalNoticeIfPending(notice, options = {}) {
  if (!notice?.pending) return false;
  await showInfoModal(
    notice.modal?.intro || "Эффект компаньона",
    notice.modal?.effect || "",
    {
      iconSrc: notice.modal?.icon || "/photo/work_room/badresult.png",
      iconAlt: notice.modal?.iconAlt || "Эффект компаньона"
    }
  );
  await consumeIlvetalNotice(options.anomalyId ?? activeRoomAnomalyId);
  return true;
}

async function showCheapTrickNoticeIfPending(notice, options = {}) {
  if (!notice?.pending) return false;
  await showInfoModal(
    notice.modal?.intro || "Поздравляем!",
    notice.modal?.effect || "Вы стали новым владельцем компаньона Чиптрик!",
    {
      iconSrc: notice.modal?.icon || "/photo/work_room/badresult.png",
      iconAlt: notice.modal?.iconAlt || "Чиптрик"
    }
  );
  await consumeCheapTrickNotice(options.anomalyId ?? activeRoomAnomalyId);
  return true;
}

function buildDetailsActionErrorMessage(actionLabel, rawMessage) {
  const raw = String(rawMessage || "").trim();
  const text = String(rawMessage || "").toLowerCase();
  if (text.includes("без активного сигнала")) {
    return `Невозможно открыть ${actionLabel}. Причина: ${raw}`;
  }
  if (text.includes("после отказа от компаньона")) {
    return `Невозможно открыть ${actionLabel}. Причина: после отказа от компаньона дальнейшее исследование невозможно.`;
  }
  if (text.includes("недостат") || text.includes("не хватает") || text.includes("rp")) {
    return `Невозможно открыть ${actionLabel}. Причина: недостаточно исследовательских очков.`;
  }
  if (
    text.includes("недоступ") ||
    text.includes("запрещ") ||
    text.includes("невозможно открыть") ||
    text.includes("эффект")
  ) {
    return `Невозможно открыть ${actionLabel}. Причина: эффект аномалии.`;
  }
  return "";
}

async function handleDetailsActionError(actionLabel, error) {
  const message = buildDetailsActionErrorMessage(actionLabel, error?.message || error);
  if (!message) {
    throw error;
  }
  await showDetailsInfoModal({
    intro: "Недопустимое действие",
    effect: message,
    icon: "/photo/work_room/neutralresult.png",
    iconAlt: "Недопустимое действие"
  });
}

async function showRuntimeErrorModal(error, options = {}) {
  const rawMessage = String(error?.message || error || "Произошла ошибка.").trim() || "Произошла ошибка.";
  const actionLabel = String(options.actionLabel || "").trim();
  let effectText = rawMessage;
  if (actionLabel) {
    effectText = buildDetailsActionErrorMessage(actionLabel, rawMessage) || rawMessage;
  }
  const modalPayload = {
    intro: "Недопустимое действие",
    effect: effectText,
    icon: "/photo/work_room/neutralresult.png",
    iconAlt: "Недопустимое действие"
  };
  if (!gameDetailsScreen.classList.contains("hidden")) {
    await showDetailsInfoModal(modalPayload);
    return;
  }
  await showInfoModal(modalPayload.intro, modalPayload.effect, {
    iconSrc: modalPayload.icon,
    iconAlt: modalPayload.iconAlt
  });
}

let utilizerNoticeShowing = false;

async function showUtilizerNoticeIfPending(notice) {
  if (!notice?.pending || utilizerNoticeShowing) return false;
  utilizerNoticeShowing = true;
  try {
    await showInfoModal(notice.title || "Утилизатор", notice.message || "Утилизатор что-то поглотил.", {
      iconSrc: "/photo/work_room/neutralresult.png",
      iconAlt: "Утилизатор"
    });
    await apiPost("/api/game/consume-utilizer-notice", { user_id: currentUserId() });
  } finally {
    utilizerNoticeShowing = false;
  }
  return true;
}

function showEventChoiceModal(config = {}) {
  if (!eventOverlay) return;
  eventIcon.classList.remove("hidden");
  eventIcon.src = config.icon || "/photo/work_room/badresult.png";
  eventIcon.alt = config.iconAlt || "Событие";
  eventIntro.textContent = config.intro || "";
  eventEffect.textContent = config.effect || "";
  eventRollerWrap.classList.add("hidden");
  eventConfirmButton.classList.add("hidden");
  eventChoices.innerHTML = (config.choices || []).map((choice, index) => `
    <button
      class="event-choice-button ${choice.className || ""}"
      type="button"
      data-event-choice-index="${index}"
      ${choice.disabled ? "disabled" : ""}
      title="${escapeHtml(choice.title || "")}"
    >${escapeHtml(choice.label || "Выбрать")}</button>
  `).join("");
  eventChoices.querySelectorAll("[data-event-choice-index]").forEach((button) => {
    const index = Number(button.dataset.eventChoiceIndex || 0);
    button.addEventListener("click", async () => {
      const choice = (config.choices || [])[index];
      if (choice?.disabled) {
        return;
      }
      if (typeof choice?.onSelect === "function") {
        await choice.onSelect();
      }
    });
  });
  eventOverlay.classList.remove("hidden");
}

async function openKillContractOffer(anomalyId) {
  const payload = await apiPost("/api/game/contract-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  const targets = Array.isArray(action.targets) ? action.targets : [];
  const choiceConfig = targets.length
    ? [
        ...targets.map((target) => ({
          label: target.label,
          onClick: async () => {
            const applyPayload = await apiPost("/api/game/contract-apply", {
              user_id: currentUserId(),
              target_id: target.id
            });
            if (!gameDetailsScreen.classList.contains("hidden")) {
              closeDetailsEventModal();
            } else {
              closeEventModal();
            }
            if (applyPayload.room) {
              renderWorkRoom(applyPayload.room);
            }
            if (applyPayload.details && !gameDetailsScreen.classList.contains("hidden")) {
              renderDetailsScreen(applyPayload.details);
            }
          }
        })),
        {
          label: "Отказаться",
          onClick: async () => {
            const declinePayload = await apiPost("/api/game/contract-decline", {
              user_id: currentUserId()
            });
            if (!gameDetailsScreen.classList.contains("hidden")) {
              closeDetailsEventModal();
            } else {
              closeEventModal();
            }
            if (declinePayload.room) renderWorkRoom(declinePayload.room);
            if (declinePayload.details && !gameDetailsScreen.classList.contains("hidden")) {
              renderDetailsScreen(declinePayload.details);
            }
          }
        }
      ]
    : [
        {
          label: "😐 Сейчас некому «передать привет».",
          onClick: async () => {
            const declinePayload = await apiPost("/api/game/contract-decline", {
              user_id: currentUserId()
            });
            if (!gameDetailsScreen.classList.contains("hidden")) {
              closeDetailsEventModal();
            } else {
              closeEventModal();
            }
            if (declinePayload.room) renderWorkRoom(declinePayload.room);
            if (declinePayload.details && !gameDetailsScreen.classList.contains("hidden")) {
              renderDetailsScreen(declinePayload.details);
            }
          }
        }
      ];
  const modalConfig = {
    icon: "/photo/work_room/badresult.png",
    iconAlt: "Предложение убийцы",
    intro: action.intro || "Предложение убийцы",
    effect: action.effect || "Вы можете заказать устранение другого сотрудника за 1000 СО. Что скажете?",
    choices: choiceConfig
  };
  if (!gameDetailsScreen.classList.contains("hidden")) {
    showDetailsChoiceModal(modalConfig);
    return;
  }
  showEventChoiceModal({
    ...modalConfig,
    choices: choiceConfig.map((choice) => ({
      ...choice,
      onSelect: choice.onClick
    }))
  });
}

async function openCurse137Offer(anomalyId = 137) {
  const payload = await apiPost("/api/details/curse137-preview", {
    user_id: currentUserId(), anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  showDetailsChoiceModal({
    icon: "/photo/work_room/badresult.png",
    iconAlt: "Создание проклятия",
    intro: action.intro || "Создание проклятия",
    effect: action.effect || "Сделайте выбор.",
    choices: (action.options || []).map((option) => ({
      label: option.label,
      onClick: async () => {
        const result = await apiPost("/api/details/curse137-choice", {
          user_id: currentUserId(), anomaly_id: anomalyId, choice: option.key
        });
        if (!result.resolved) {
          await openCurse137Offer(anomalyId);
          return;
        }
        closeDetailsEventModal();
        if (result.details) renderDetailsScreen(result.details);
        if (result.room) renderWorkRoom(result.room);
        await showInfoModal("Сделка заключена", `${result.message}\n\nУсловие: ${result.trigger}\nПоследствие: ${result.consequence}`);
      }
    }))
  });
}

async function openStatConversionOffer(anomalyId) {
  const payload = await apiPost("/api/game/stat-conversion-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  const choiceConfig = [
    ...(Array.isArray(action.options) ? action.options : []).map((option) => ({
      label: option.label,
      disabled: !!option.disabled,
      title: option.blocked_reason || "",
      onClick: async () => {
        const applyPayload = await apiPost("/api/game/stat-conversion-apply", {
          user_id: currentUserId(),
          stat_key: option.key
        });
        closeDetailsEventModal();
        if (applyPayload.room) {
          renderWorkRoom(applyPayload.room);
        }
        if (applyPayload.details) {
          renderDetailsScreen(applyPayload.details);
        }
      }
    })),
    {
      label: "Отказаться",
      onClick: async () => {
        const declinePayload = await apiPost("/api/game/stat-conversion-decline", {
          user_id: currentUserId()
        });
        closeDetailsEventModal();
        if (declinePayload.room) renderWorkRoom(declinePayload.room);
        if (declinePayload.details) renderDetailsScreen(declinePayload.details);
      }
    }
  ];
  showDetailsChoiceModal({
    icon: "/photo/work_room/goodresult.png",
    iconAlt: "Обмен",
    intro: action.intro || "Обмен",
    effect: action.effect || "Вы можете обменять 1 очко Удачи, Гибкости ума или Адаптации на +1 к Выносливости. Согласиться?",
    choices: choiceConfig
  });
}

async function openDeathShieldOffer(anomalyId) {
  const payload = await apiPost("/api/game/death-shield-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  showDetailsChoiceModal({
    icon: action.icon || "/photo/work_room/neutralresult.png",
    iconAlt: action.iconAlt || "Сделка",
    intro: action.intro || "Сделка",
    effect: action.effect || "",
    choices: [
      {
        label: "Да",
        disabled: !action.can_accept,
        title: action.blocked_reason || "",
        onClick: async () => {
          const applyPayload = await apiPost("/api/game/death-shield-apply", {
            user_id: currentUserId()
          });
          closeDetailsEventModal();
          if (applyPayload.details) {
            renderDetailsScreen(applyPayload.details);
          }
          if (applyPayload.room) {
            renderWorkRoom(applyPayload.room);
            publishCameraState("room", applyPayload.room.anomaly_id || activeRoomAnomalyId, true);
          }
        }
      },
      {
        label: "Нет",
        onClick: async () => {
          const declinePayload = await apiPost("/api/game/death-shield-decline", {
            user_id: currentUserId()
          });
          closeDetailsEventModal();
          if (declinePayload.details) renderDetailsScreen(declinePayload.details);
          if (declinePayload.room) renderWorkRoom(declinePayload.room);
        }
      }
    ]
  });
}

async function openAltarOffering(anomalyId) {
  const payload = await apiPost("/api/game/altar-offering-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  showDetailsChoiceModal({
    icon: action.icon || "/photo/work_room/neutralresult.png",
    iconAlt: action.iconAlt || "Алтарь угля",
    intro: action.intro || "Подношение Алтарю угля",
    effect: action.effect || "Хотите сделать подношение в виде крови?",
    choices: [
      {
        label: "Потратить 10 HP",
        disabled: !action.can_accept,
        title: action.blocked_reason || "",
        onClick: async () => {
          const result = await apiPost("/api/game/altar-offering-apply", { user_id: currentUserId() });
          closeDetailsEventModal();
          applyDamageFeedback(result);
          if (result.damage?.shield_triggered) await showDeathShieldMiracleModal(result.damage);
          if (result.player_dead) {
            await showDeathModal(result.death_reason || "Сотрудник погиб во время подношения.");
            if (showFinalResults(result.final_results || result.game_state?.final_results)) return;
            if (result.game_state?.game?.started) await applyGameState(result.game_state, { forceRefresh: true });
            return;
          }
          if (result.details) renderDetailsScreen(result.details);
          if (result.room) renderWorkRoom(result.room);
        }
      },
      {
        label: "Отказаться",
        onClick: () => closeDetailsEventModal()
      }
    ]
  });
}

async function openDevilDeal(anomalyId) {
  const payload = await apiPost("/api/game/devil-deal-preview", {
    user_id: currentUserId(), anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  showDetailsChoiceModal({
    icon: action.icon || "/photo/anomaly/041_devil.png",
    iconAlt: action.iconAlt || "Дьявол",
    intro: action.intro || "Сделка",
    effect: action.effect || "Душа в обмен на знания.",
    choices: [
      {
        label: "Согласиться",
        onClick: async () => {
          const result = await apiPost("/api/game/devil-deal-resolve", {
            user_id: currentUserId(), accept: true
          });
          closeDetailsEventModal();
          if (result.details) renderDetailsScreen(result.details);
          if (result.room) renderWorkRoom(result.room);
        }
      },
      {
        label: "Отказаться",
        onClick: async () => {
          const result = await apiPost("/api/game/devil-deal-resolve", {
            user_id: currentUserId(), accept: false
          });
          closeDetailsEventModal();
          applyDamageFeedback(result);
          if (result.damage?.shield_triggered) await showDeathShieldMiracleModal(result.damage);
          if (result.player_dead) {
            await showDeathModal(result.death_reason || "Сгинул в преисподней");
            if (showFinalResults(result.final_results || result.game_state?.final_results)) return;
            if (result.game_state?.game?.started) await applyGameState(result.game_state, { forceRefresh: true });
            return;
          }
          if (result.details) renderDetailsScreen(result.details);
          if (result.room) renderWorkRoom(result.room);
        }
      }
    ]
  });
}

async function openFreeStatOffer(anomalyId) {
  const payload = await apiPost("/api/game/free-stat-preview", {
    user_id: currentUserId(), anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  const iconByStat = { STAT1: "💪", STAT2: "🍀", STAT3: "🧠", STAT4: "🛡" };
  showDetailsChoiceModal({
    icon: action.icon || "/photo/anomaly/049_toiletgod.png",
    iconAlt: action.iconAlt || "Дар характеристики",
    intro: action.intro || "Дар характеристики",
    effect: action.effect || "Выберите характеристику, которую хотите повысить на 1.",
    choices: (action.options || []).map((option) => ({
      label: `${iconByStat[option.key] || ""} ${option.label} (${Number(option.level || 1)} → ${Math.min(5, Number(option.level || 1) + 1)})`,
      disabled: !option.can_choose,
      title: option.can_choose ? "" : "Характеристика уже на максимуме",
      onClick: async () => {
        const result = await apiPost("/api/game/free-stat-apply", {
          user_id: currentUserId(), stat_key: option.key
        });
        closeDetailsEventModal();
        await showInfoModal(
          "Дар получен",
          `${result.stat_name} повышена до ${result.new_level}.`,
          { iconSrc: action.icon || "/photo/anomaly/049_toiletgod.png", iconAlt: "Дар характеристики" }
        );
        if (result.details) renderDetailsScreen(result.details);
        if (result.room) renderWorkRoom(result.room);
      }
    }))
  });
}

const MOON_EYE_COLOR_LABELS = { red: "красный", yellow: "жёлтый", purple: "фиолетовый" };
const moonEyeFrame = (color, frame = 12) => `/photo/VN/veyeral/${color}${frame}.png`;
const waitMoonEye = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));

function ensureMoonEyeOverlay() {
  let overlay = document.getElementById("moonEyeOverlay");
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.id = "moonEyeOverlay";
  overlay.className = "moon-eye-overlay hidden";
  overlay.innerHTML = `
    <div class="moon-eye-stage">
      <div class="moon-eye-instruction" id="moonEyeInstruction"></div>
      <div class="moon-eye-timer hidden" id="moonEyeTimer"></div>
      <div class="moon-eye-field" id="moonEyeField"></div>
      <form class="moon-eye-question hidden" id="moonEyeQuestion">
        <label id="moonEyeQuestionText" for="moonEyeAnswer"></label>
        <div class="moon-eye-answer-row">
          <input id="moonEyeAnswer" type="number" min="0" max="25" required inputmode="numeric" autocomplete="off">
          <button type="submit">Ответить</button>
        </div>
      </form>
      <button class="moon-eye-stop hidden" id="moonEyeStop" type="button">СТОП</button>
      <button class="moon-eye-start" id="moonEyeStart" type="button">Начать</button>
    </div>`;
  document.body.appendChild(overlay);
  return overlay;
}

async function animateMoonEye(img, color, closeAfter = false, frameDelay = 45) {
  for (let frame = 1; frame <= 12; frame += 1) {
    img.src = moonEyeFrame(color, frame);
    await waitMoonEye(frameDelay);
  }
  if (!closeAfter) return;
  await waitMoonEye(90);
  for (let frame = 11; frame >= 1; frame -= 1) {
    img.src = moonEyeFrame(color, frame);
    await waitMoonEye(frameDelay);
  }
}

function playMoonEyeSound(filename) {
  const audio = new Audio(`/sound/${filename}`);
  audio.volume = 0.8;
  audio.play().catch(() => {});
  return audio;
}

function askMoonEyeQuestion(round, seconds = 15) {
  const form = document.getElementById("moonEyeQuestion");
  const input = document.getElementById("moonEyeAnswer");
  const timer = document.getElementById("moonEyeTimer");
  document.getElementById("moonEyeQuestionText").textContent = round.question;
  input.value = "";
  input.max = String(round.eyes.length);
  form.classList.remove("hidden");
  timer.classList.remove("hidden");
  input.focus();
  return new Promise((resolve) => {
    let remaining = seconds;
    timer.textContent = String(remaining);
    playMoonEyeSound("clock_1.wav");
    const interval = window.setInterval(() => {
      remaining -= 1;
      timer.textContent = String(Math.max(0, remaining));
      if (remaining === 10) playMoonEyeSound("clock_2.wav");
      if (remaining === 5) playMoonEyeSound("clock_3.wav");
      if (remaining > 0) return;
      window.clearInterval(interval);
      form.classList.add("hidden");
      timer.classList.add("hidden");
      form.onsubmit = null;
      resolve(null);
    }, 1000);
    form.onsubmit = (event) => {
      event.preventDefault();
      const answer = Number(input.value);
      if (!Number.isInteger(answer) || answer < 0 || answer > round.eyes.length) return;
      window.clearInterval(interval);
      form.classList.add("hidden");
      timer.classList.add("hidden");
      resolve(answer);
    };
  });
}

async function playMoonEyeRound(round) {
  const field = document.getElementById("moonEyeField");
  const instruction = document.getElementById("moonEyeInstruction");
  field.innerHTML = "";
  instruction.textContent = round.instruction;
  await waitMoonEye(1300);
  if (round.type === "reaction") {
    const stopButton = document.getElementById("moonEyeStop");
    stopButton.classList.remove("hidden");
    let stopIndex = null;
    stopButton.onclick = () => { stopIndex = activeIndex; };
    let activeIndex = -1;
    for (let index = 0; index < round.eyes.length && stopIndex === null; index += 1) {
      const color = round.eyes[index];
      activeIndex = index;
      const img = document.createElement("img");
      img.className = "moon-eye-single";
      img.alt = `${MOON_EYE_COLOR_LABELS[color]} глаз`;
      field.replaceChildren(img);
      const delay = 48 - Math.min(index, 9) * 3;
      for (let frame = 1; frame <= 12 && stopIndex === null; frame += 1) {
        img.src = moonEyeFrame(color, frame);
        await waitMoonEye(delay);
      }
      for (let frame = 11; frame >= 1 && stopIndex === null; frame -= 1) {
        img.src = moonEyeFrame(color, frame);
        await waitMoonEye(delay);
      }
    }
    stopButton.classList.add("hidden");
    stopButton.onclick = null;
    field.innerHTML = "";
    return stopIndex;
  } else if (round.type === "fall") {
    await Promise.all(round.eyes.map(async (color, index) => {
      await waitMoonEye(index * 120);
      const img = document.createElement("img");
      img.className = "moon-eye-falling";
      img.src = moonEyeFrame(color, 12);
      img.alt = `${MOON_EYE_COLOR_LABELS[color]} глаз`;
      img.style.left = `${5 + Math.random() * 82}%`;
      img.style.animationDuration = `${1.35 + Math.random() * 0.7}s`;
      field.appendChild(img);
      await waitMoonEye(2200);
    }));
    field.innerHTML = "";
  } else {
    const positions = [{ x: 50, y: 50, layer: 0 }];
    for (let i = 0; i < 8; i += 1) {
      const angle = (Math.PI * 2 * i) / 8;
      positions.push({ x: 50 + Math.cos(angle) * 20, y: 50 + Math.sin(angle) * 25, layer: 1 });
    }
    for (let i = 0; i < 16; i += 1) {
      const angle = (Math.PI * 2 * i) / 16;
      positions.push({ x: 50 + Math.cos(angle) * 42, y: 50 + Math.sin(angle) * 43, layer: 2 });
    }
    const layerHoldTimes = [1000, 2000, 4000];
    for (let layer = 0; layer <= 2; layer += 1) {
      const items = positions.map((position, index) => ({ position, color: round.eyes[index] }))
        .filter((item) => item.position.layer === layer);
      await Promise.all(items.map(async ({ position, color }) => {
        const img = document.createElement("img");
        img.className = `moon-eye-ring layer-${layer}`;
        img.style.left = `${position.x}%`;
        img.style.top = `${position.y}%`;
        img.alt = `${MOON_EYE_COLOR_LABELS[color]} глаз`;
        field.appendChild(img);
        await animateMoonEye(img, color, false, 28);
      }));
      await waitMoonEye(layerHoldTimes[layer]);
    }
    await waitMoonEye(900);
    field.innerHTML = "";
  }
  instruction.textContent = "";
  return askMoonEyeQuestion(round, 15);
}

async function showMoonEyeRoundResult(result) {
  const instruction = document.getElementById("moonEyeInstruction");
  const field = document.getElementById("moonEyeField");
  field.innerHTML = "";
  if (result.correct) {
    playMoonEyeSound("012. Deep HiTech UI Sound 3.wav");
    instruction.textContent = "ВЕРНО";
  } else {
    playMoonEyeSound("OverloadAlert3.wav");
    instruction.textContent = result.reaction_timeout
      ? "ЗАДАНИЕ НЕ ВЫПОЛНЕНО. НЕВЕРНО. Несовершенству нет здесь места!"
      : "НЕВЕРНО. Несовершенству нет здесь места!";
    applyDamageFeedback(result);
  }
  await waitMoonEye(1800);
}

async function startMoonEyeGame(anomalyId) {
  const payload = await apiPost("/api/game/moon-eye-start", { user_id: currentUserId(), anomaly_id: anomalyId });
  await Promise.all(["red", "yellow", "purple"].flatMap((color) =>
    Array.from({ length: 12 }, (_, index) => new Promise((resolve) => {
      const image = new Image();
      image.onload = resolve;
      image.onerror = resolve;
      image.src = moonEyeFrame(color, index + 1);
    }))
  ));
  const overlay = ensureMoonEyeOverlay();
  const startButton = document.getElementById("moonEyeStart");
  const instruction = document.getElementById("moonEyeInstruction");
  const field = document.getElementById("moonEyeField");
  overlay.classList.remove("hidden");
  instruction.textContent = "Вейерал хочет проверить вашу внимательность";
  field.innerHTML = "";
  startButton.classList.remove("hidden");
  await new Promise((resolve) => { startButton.onclick = resolve; });
  startButton.classList.add("hidden");
  let result = null;
  for (let index = 0; index < (payload.rounds || []).length; index += 1) {
    const answer = await playMoonEyeRound(payload.rounds[index]);
    result = await apiPost("/api/game/moon-eye-resolve", {
      user_id: currentUserId(), challenge_id: payload.challenge_id, round_index: index, answer
    });
    await showMoonEyeRoundResult(result);
    if (result.player_dead) break;
  }
  overlay.classList.add("hidden");
  if (result?.player_dead) {
    await showDeathModal(result.death_reason || "Несовершенству нет здесь места!");
    if (showFinalResults(result.final_results || result.game_state?.final_results)) return;
    if (result.game_state?.game?.started) await applyGameState(result.game_state, { forceRefresh: true });
    return;
  }
  if (result.details) renderDetailsScreen(result.details);
  if (result.room) renderWorkRoom(result.room);
}

function ensureEmojiGlassesOverlay() {
  let overlay = document.getElementById("emojiGlassesOverlay");
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.id = "emojiGlassesOverlay";
  overlay.className = "emoji-glasses-overlay hidden";
  overlay.innerHTML = `
    <div class="emoji-glasses-stage" id="emojiGlassesStage">
      <div class="emoji-glasses-title">Перетащи очки на лицо</div>
      <div class="emoji-glasses-timer" id="emojiGlassesTimer">10</div>
      <div class="emoji-maze-wall wall-one" data-maze-wall></div>
      <div class="emoji-maze-wall wall-two" data-maze-wall></div>
      <div class="emoji-maze-wall wall-three" data-maze-wall></div>
      <div class="emoji-maze-wall wall-four" data-maze-wall></div>
      <div class="emoji-maze-wall wall-five" data-maze-wall></div>
      <div class="emoji-face-target" id="emojiFaceTarget">
        <img src="/photo/special/smile.png" alt="Лицо">
      </div>
      <img class="emoji-drag-glasses" id="emojiDragGlasses" src="/photo/special/glasses.png?v=2" alt="Очки">
    </div>`;
  document.body.appendChild(overlay);
  return overlay;
}

function renderSpectatorEmojiGame(state = {}) {
  document.getElementById("seaMonsterOverlay")?.classList.add("hidden");
  const overlay = ensureEmojiGlassesOverlay();
  overlay.classList.add("spectator-copy");
  const glasses = document.getElementById("emojiDragGlasses");
  const timer = document.getElementById("emojiGlassesTimer");
  overlay.classList.remove("hidden");
  glasses.style.left = `${Math.max(0, Math.min(100, Number(state.left ?? 5)))}%`;
  glasses.style.top = `${Math.max(0, Math.min(100, Number(state.top ?? 80)))}%`;
  glasses.style.transform = "none";
  timer.textContent = String(Math.max(0, Number(state.remaining ?? 10)));
}

async function startEmojiGlassesGame(anomalyId) {
  const payload = await apiPost("/api/game/emoji-glasses-start", {
    user_id: currentUserId(), anomaly_id: anomalyId
  });
  const overlay = ensureEmojiGlassesOverlay();
  overlay.classList.remove("spectator-copy");
  const stage = document.getElementById("emojiGlassesStage");
  const glasses = document.getElementById("emojiDragGlasses");
  const face = document.getElementById("emojiFaceTarget");
  const timer = document.getElementById("emojiGlassesTimer");
  glasses.style.left = "5%";
  glasses.style.top = "80%";
  glasses.style.transform = "none";
  overlay.classList.remove("hidden");
  let finished = false;
  let dragging = false;
  let dragOffsetX = 0;
  let dragOffsetY = 0;
  let lastCameraPublish = 0;
  const publishEmoji = (force = false) => {
    const now = performance.now();
    if (!force && now - lastCameraPublish < 100) return;
    lastCameraPublish = now;
    const stageRect = stage.getBoundingClientRect();
    const rect = glasses.getBoundingClientRect();
    publishCameraState("emoji_game", anomalyId, true, { mini_game_state: {
      left: stageRect.width ? (rect.left - stageRect.left) / stageRect.width * 100 : 5,
      top: stageRect.height ? (rect.top - stageRect.top) / stageRect.height * 100 : 80,
      remaining
    }});
  };

  const collides = (left, top) => {
    const stageRect = stage.getBoundingClientRect();
    const width = glasses.offsetWidth;
    const height = glasses.offsetHeight;
    const candidate = { left: stageRect.left + left, right: stageRect.left + left + width, top: stageRect.top + top, bottom: stageRect.top + top + height };
    if (left < 0 || top < 0 || left + width > stageRect.width || top + height > stageRect.height) return true;
    return [...stage.querySelectorAll("[data-maze-wall]")].some((wall) => {
      const rect = wall.getBoundingClientRect();
      return candidate.left < rect.right && candidate.right > rect.left && candidate.top < rect.bottom && candidate.bottom > rect.top;
    });
  };

  const moveToward = (targetLeft, targetTop) => {
    const stageRect = stage.getBoundingClientRect();
    const currentRect = glasses.getBoundingClientRect();
    let left = currentRect.left - stageRect.left;
    let top = currentRect.top - stageRect.top;
    const distance = Math.hypot(targetLeft - left, targetTop - top);
    const steps = Math.max(1, Math.ceil(distance / 4));
    for (let step = 1; step <= steps; step += 1) {
      const nextLeft = left + (targetLeft - left) / (steps - step + 1);
      const nextTop = top + (targetTop - top) / (steps - step + 1);
      if (collides(nextLeft, nextTop)) {
        glasses.style.left = "5%";
        glasses.style.top = "80%";
        glasses.classList.remove("maze-hit");
        void glasses.offsetWidth;
        glasses.classList.add("maze-hit");
        dragging = false;
        return;
      }
      left = nextLeft;
      top = nextTop;
    }
    glasses.style.left = `${left}px`;
    glasses.style.top = `${top}px`;
  };

  let remaining = Number(payload.duration || 10);
  timer.textContent = String(remaining);
  publishEmoji(true);
  const settle = async (success) => {
    if (finished) return;
    finished = true;
    window.clearInterval(countdown);
    overlay.classList.add("hidden");
    const result = await apiPost("/api/game/emoji-glasses-resolve", {
      user_id: currentUserId(), challenge_id: payload.challenge_id, success
    });
    applyDamageFeedback(result);
    if (result.damage?.shield_triggered) await showDeathShieldMiracleModal(result.damage);
    if (result.player_dead) {
      await showDeathModal(result.death_reason || "Не успел надеть очки во время затмения");
      if (showFinalResults(result.final_results || result.game_state?.final_results)) return;
      if (result.game_state?.game?.started) await applyGameState(result.game_state, { forceRefresh: true });
      return;
    }
    await showInfoModal(success ? "Успех" : "Время вышло", result.message || "Испытание завершено.", {
      iconSrc: success ? "/photo/special/glasses.png" : "/photo/work_room/fail.png",
      iconAlt: success ? "Очки надеты" : "Испытание провалено"
    });
    if (result.details) renderDetailsScreen(result.details);
    if (result.room) renderWorkRoom(result.room);
  };
  const countdown = window.setInterval(() => {
    remaining -= 1;
    timer.textContent = String(Math.max(0, remaining));
    publishEmoji(true);
    if (remaining <= 0) settle(false).catch((error) => showRuntimeErrorModal(error));
  }, 1000);

  glasses.onpointerdown = (event) => {
    if (finished) return;
    dragging = true;
    glasses.classList.remove("maze-hit");
    const rect = glasses.getBoundingClientRect();
    dragOffsetX = event.clientX - rect.left;
    dragOffsetY = event.clientY - rect.top;
    glasses.setPointerCapture(event.pointerId);
    event.preventDefault();
  };
  glasses.onpointermove = (event) => {
    if (!dragging || finished) return;
    const stageRect = stage.getBoundingClientRect();
    moveToward(event.clientX - stageRect.left - dragOffsetX, event.clientY - stageRect.top - dragOffsetY);
    publishEmoji();
  };
  glasses.onpointerup = (event) => {
    if (!dragging || finished) return;
    dragging = false;
    glasses.releasePointerCapture(event.pointerId);
    const glassesRect = glasses.getBoundingClientRect();
    const faceRect = face.getBoundingClientRect();
    const centerX = glassesRect.left + glassesRect.width / 2;
    const centerY = glassesRect.top + glassesRect.height / 2;
    if (centerX >= faceRect.left && centerX <= faceRect.right && centerY >= faceRect.top && centerY <= faceRect.bottom) {
      settle(true).catch((error) => showRuntimeErrorModal(error));
    }
  };
}

function ensureSeaMonsterOverlay() {
  let overlay = document.getElementById("seaMonsterOverlay");
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.id = "seaMonsterOverlay";
  overlay.className = "sea-monster-overlay hidden";
  overlay.innerHTML = `
    <div class="sea-monster-header">
      <div id="seaMonsterRound">АТАКА 1 / 5</div>
      <div id="seaMonsterStatus">СТРЕЛКИ ← → — ПЕРЕМЕЩЕНИЕ ЩИТА</div>
    </div>
    <div class="sea-monster-field" id="seaMonsterField">
      <div class="sea-monster-grid" aria-hidden="true"></div>
      <img class="sea-monster-sprite" id="seaMonsterSprite" src="/photo/special/leviathan.png" alt="Левиафан">
      <img class="sea-monster-shield" id="seaMonsterShield" src="/photo/special/shield.png" alt="Щит">
    </div>
    <div class="sea-monster-controls">
      <button type="button" data-sea-move="-1" aria-label="Передвинуть щит влево">←</button>
      <button type="button" data-sea-move="1" aria-label="Передвинуть щит вправо">→</button>
    </div>`;
  document.body.appendChild(overlay);
  return overlay;
}

function renderSpectatorSeaGame(state = {}) {
  document.getElementById("emojiGlassesOverlay")?.classList.add("hidden");
  const overlay = ensureSeaMonsterOverlay();
  overlay.classList.add("spectator-copy");
  const monster = document.getElementById("seaMonsterSprite");
  const shield = document.getElementById("seaMonsterShield");
  const roundLabel = document.getElementById("seaMonsterRound");
  const status = document.getElementById("seaMonsterStatus");
  const bounds = { left: 26.37, top: 3.32, width: 47.46, height: 83.85 };
  const place = (element, column, row) => {
    element.style.left = `${bounds.left + Math.max(0, Math.min(2, Number(column || 0))) * (bounds.width / 3)}%`;
    element.style.top = `${bounds.top + Math.max(0, Math.min(11, Number(row || 0))) * (bounds.height / 12)}%`;
  };
  overlay.classList.remove("hidden");
  overlay.querySelector(".sea-monster-controls")?.classList.add("hidden");
  roundLabel.textContent = `АТАКА ${Math.max(1, Number(state.round || 1))} / 5`;
  status.textContent = state.status || "ИГРОК ВЫСТАВЛЯЕТ ЩИТ";
  place(monster, state.monster_column, state.monster_row);
  place(shield, state.shield_column ?? 1, 11);
}

async function startSeaMonsterGame(anomalyId) {
  await showVnChoiceModal({
    nameplate: "",
    speaker: "",
    portrait: "",
    characterVisible: false,
    background: null,
    darkScene: true,
    text: "Похоже, что объект 62 необходимо сдержать. Выставляйте щит прямо перед атакой в области, где находится левиафан. Для этого у вас на экране будут отражены сектора и местонахождение чудища.",
    confirmOnly: true,
    confirmLabel: "Начать",
    speed: 18
  });
  const payload = await apiPost("/api/game/sea-monster-start", {
    user_id: currentUserId(), anomaly_id: anomalyId
  });
  await Promise.all(["field.png", "leviathan.png", "shield.png"].map((name) => new Promise((resolve) => {
    const image = new Image();
    image.onload = resolve;
    image.onerror = resolve;
    image.src = `/photo/special/${name}`;
  })));
  const overlay = ensureSeaMonsterOverlay();
  overlay.classList.remove("spectator-copy");
  const field = document.getElementById("seaMonsterField");
  const monster = document.getElementById("seaMonsterSprite");
  const shield = document.getElementById("seaMonsterShield");
  const roundLabel = document.getElementById("seaMonsterRound");
  const status = document.getElementById("seaMonsterStatus");
  let shieldColumn = 1;
  let currentRound = Number(payload.round || 1);
  let stopped = false;
  let monsterColumn = 1;
  let monsterRow = 0;
  const publishSea = (message = "") => publishCameraState("sea_game", anomalyId, true, { mini_game_state: {
    round: currentRound, shield_column: shieldColumn, monster_column: monsterColumn,
    monster_row: monsterRow, status: message || status.textContent || ""
  }});

  // The playable 3x12 grid occupies only the central part of field.png.
  // Keep both sprites inside the actual painted cells, not the full image.
  const gridBounds = { left: 26.37, top: 3.32, width: 47.46, height: 83.85 };
  const place = (element, column, row) => {
    element.style.left = `${gridBounds.left + column * (gridBounds.width / 3)}%`;
    element.style.top = `${gridBounds.top + row * (gridBounds.height / 12)}%`;
  };
  const moveShield = (direction) => {
    if (stopped) return;
    shieldColumn = Math.max(0, Math.min(2, shieldColumn + Number(direction || 0)));
    place(shield, shieldColumn, 11);
    publishSea();
  };
  const keyHandler = (event) => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      moveShield(event.key === "ArrowLeft" ? -1 : 1);
    }
  };
  overlay.querySelectorAll("[data-sea-move]").forEach((button) => {
    button.onclick = () => moveShield(Number(button.dataset.seaMove));
  });
  window.addEventListener("keydown", keyHandler);
  overlay.classList.remove("hidden");
  overlay.querySelector(".sea-monster-controls")?.classList.remove("hidden");
  place(shield, shieldColumn, 11);
  publishSea();

  const wait = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  try {
    while (!stopped && currentRound <= 5) {
      roundLabel.textContent = `АТАКА ${currentRound} / 5`;
      status.textContent = "СТРЕЛКИ ← → — ПЕРЕМЕЩЕНИЕ ЩИТА";
      status.classList.remove("success", "failed");
      const speed = Math.max(280, 700 - (currentRound - 1) * 105);
      monster.style.transitionDuration = `${Math.round(speed * 0.72)}ms`;
      monsterColumn = Math.floor(Math.random() * 3);
      monsterRow = 0;
      const finalColumn = Math.floor(Math.random() * 3);
      place(monster, monsterColumn, 0);
      publishSea();
      await wait(350);
      for (let row = 1; row <= 11; row += 1) {
        await wait(speed);
        if (row < 11) {
          const moves = [-1, 0, 1].filter((delta) => monsterColumn + delta >= 0 && monsterColumn + delta <= 2);
          if (row === 10) {
            monsterColumn += Math.sign(finalColumn - monsterColumn);
          } else {
            const nonStationary = moves.filter((delta) => delta !== 0);
            const pool = nonStationary.length && Math.random() < 0.72 ? nonStationary : moves;
            monsterColumn += pool[Math.floor(Math.random() * pool.length)];
          }
        } else {
          monsterColumn = finalColumn;
        }
        place(monster, monsterColumn, row);
        monsterRow = row;
        publishSea();
      }
      await wait(Math.round(speed * 0.75));
      const success = shieldColumn === monsterColumn;
      const result = await apiPost("/api/game/sea-monster-resolve", {
        user_id: currentUserId(), challenge_id: payload.challenge_id, success
      });
      if (result.damage) {
        applyDamageFeedback(result);
        if (result.damage.shield_triggered) await showDeathShieldMiracleModal(result.damage);
      }
      if (result.player_dead) {
        stopped = true;
        overlay.classList.add("hidden");
        await showDeathModal(result.death_reason || "Не смог отразить атаку Морского дьявола");
        if (showFinalResults(result.final_results || result.game_state?.final_results)) return;
        if (result.game_state?.game?.started) await applyGameState(result.game_state, { forceRefresh: true });
        return;
      }
      status.textContent = result.message || (success ? "АТАКА ОТРАЖЕНА" : "ПРОМАХ — ПОЛУЧЕНО 75 УРОНА");
      status.classList.add(success ? "success" : "failed");
      publishSea(status.textContent);
      if (success && result.finished) {
        stopped = true;
        await wait(1100);
        overlay.classList.add("hidden");
        await showInfoModal("Победа", "Все пять атак Морского дьявола отражены.", {
          iconSrc: "/photo/special/shield.png", iconAlt: "Щит"
        });
        if (result.room) renderWorkRoom(result.room);
        return;
      }
      if (success) currentRound = Number(result.round || currentRound + 1);
      await wait(success ? 850 : 1100);
    }
  } finally {
    window.removeEventListener("keydown", keyHandler);
    overlay.classList.add("hidden");
  }
}

async function openAlastorDeal(anomalyId) {
  const payload = await apiPost("/api/game/alastor-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  const action = payload?.action || {};
  const initialText = "Как насчёт небольшой сделки?\nЯ буду давать тебе простые задания, а взамен ты будешь зарабатывать ценные награды.";
  const refusalText = "Твоя глупость будет стоить тебе руки (*Потеряно 50 хп*). А теперь подумай ещё раз.";
  const acceptedText = "Отлично. Тогда приступай";
  const openOffer = (textOverride = null, confirmOnly = false) => showVnChoiceModal({
    nameplate: "Аластор",
    speaker: "",
    portrait: "/photo/VN/alastor1.png",
    background: "/photo/VN/VN_anomalyinteraction.png",
    text: textOverride ?? (
      action.accepted ? acceptedText : (Number(action.refusals || 0) >= 1 ? refusalText : initialText)
    ),
    confirmOnly,
    confirmLabel: "ОК",
    choices: confirmOnly ? [] : [
      {
        label: "Отказаться",
        onClick: async () => {
          const refusePayload = await apiPost("/api/game/alastor-apply", {
            user_id: currentUserId(),
            choice: "refuse"
          });
          if (refusePayload.result === "refused_once") {
            playSound("boneAttack");
            triggerDamageFlash();
            if (refusePayload.room) {
              renderWorkRoom(refusePayload.room);
            }
            if (refusePayload.player_dead) {
              await closeVnModal();
              await showDeathModal(refusePayload.death_reason || "Сотрудник погиб.");
              if (showFinalResults(refusePayload.game_state?.final_results)) {
                return;
              }
              if (refusePayload.game_state?.game?.started) {
                await applyGameState(refusePayload.game_state, { forceRefresh: true });
                return;
              }
              closeGameScreen();
              closeOnlineScreen();
              closePlayScreen();
              return;
            }
            await closeVnModal();
            await openOffer(refusalText);
            return;
          }
          if (refusePayload.result === "killed") {
            playSound("bossDead");
            await closeVnModal();
            await showDeathModal(refusePayload.death_reason || "Ты думал, что можешь отказаться?");
            if (showFinalResults(refusePayload.final_results || refusePayload.game_state?.final_results)) {
              return;
            }
            if (refusePayload.game_state?.game?.started) {
              await applyGameState(refusePayload.game_state, { forceRefresh: true });
              return;
            }
            closeGameScreen();
            closeOnlineScreen();
            closePlayScreen();
          }
        }
      },
      {
        label: "Согласиться",
        onClick: async () => {
          const acceptPayload = await apiPost("/api/game/alastor-apply", {
            user_id: currentUserId(),
            choice: "accept"
          });
          if (acceptPayload.room) {
            renderWorkRoom(acceptPayload.room);
          }
          await closeVnModal();
          await showVnChoiceModal({
            nameplate: "Аластор",
            speaker: "",
            portrait: "/photo/VN/alastor1.png",
            background: "/photo/VN/VN_anomalyinteraction.png",
            text: acceptedText,
            confirmOnly: true,
            confirmLabel: "ОК"
          });
        }
      }
    ]
  });

  if (action.accepted) {
    await openOffer(acceptedText, true);
    return;
  }
  await openOffer(Number(action.refusals || 0) >= 1 ? refusalText : initialText);
}

async function showAlastorTaskIfPending(room) {
  const prompt = room?.alastor_task;
  if (!prompt?.pending) {
    alastorTaskSignature = "";
    return false;
  }
  const signature = `${Number(prompt.task_id || 0)}:${Number(prompt.mood || 0)}:${Number(room?.anomaly_id || 0)}`;
  if (alastorTaskSignature === signature) {
    return false;
  }
  alastorTaskSignature = signature;
  await showVnChoiceModal({
    nameplate: "Аластор",
    speaker: "",
    portrait: prompt.portrait || "/photo/VN/alastor1.png",
    background: prompt.background || null,
    text: prompt.text || "",
    confirmOnly: true,
    confirmLabel: prompt.confirm_label || "ОК",
    choices: prompt.confirm_only ? [] : []
  });
  if (prompt.confirm_only) {
    const payload = await apiPost("/api/game/alastor-task-ack", {
      user_id: currentUserId(),
      anomaly_id: room?.anomaly_id
    });
    closeVnModal();
    if (payload.player_dead) {
      await showDeathModal(payload.death_reason || "Сотрудник погиб.");
      if (showFinalResults(payload.final_results || payload.game_state?.final_results)) {
        return true;
      }
      if (payload.game_state?.game?.started) {
        await applyGameState(payload.game_state, { forceRefresh: true });
        return true;
      }
      closeGameScreen();
      closeOnlineScreen();
      closePlayScreen();
      return true;
    }
  }
  return true;
}

async function showAlastorResolutionIfPending(resolution) {
  if (!resolution?.pending) {
    return false;
  }
  await showVnChoiceModal({
    nameplate: resolution.nameplate || "Аластор",
    speaker: "",
    portrait: resolution.portrait || "/photo/VN/alastor1.png",
    background: resolution.background || null,
    text: resolution.text || "",
    confirmOnly: true,
    confirmLabel: resolution.confirm_label || "ОК"
  });
  if (resolution.final_task) {
    const payload = await apiPost("/api/game/alastor-final-ack", {
      user_id: currentUserId()
    });
    closeVnModal();
    if (payload.player_dead) {
      await showDeathModal(payload.death_reason || "Сотрудник погиб.");
      if (showFinalResults(payload.final_results || payload.game_state?.final_results)) return payload;
      if (payload.game_state?.game?.started) {
        await applyGameState(payload.game_state, { forceRefresh: true });
      }
    }
    return payload;
  }
  return true;
}

async function showAlastorTaskFromGameStateIfPending(payload) {
  const prompt = payload?.alastor_task;
  if (!prompt?.pending) {
    alastorTaskSignature = "";
    return false;
  }
  const signature = `select:${Number(prompt.task_id || 0)}:${Number(prompt.mood || 0)}:${Number(payload?.game?.current_day || 0)}`;
  if (alastorTaskSignature === signature) {
    return false;
  }
  alastorTaskSignature = signature;
  await showVnChoiceModal({
    nameplate: "Аластор",
    speaker: "",
    portrait: prompt.portrait || "/photo/VN/alastor1.png",
    background: prompt.background || null,
    text: prompt.text || "",
    confirmOnly: true,
    confirmLabel: prompt.confirm_label || "ОК"
  });
  const ackPayload = await apiPost("/api/game/alastor-task-ack", {
    user_id: currentUserId()
  });
  closeVnModal();
  if (ackPayload.player_dead) {
    await showDeathModal(ackPayload.death_reason || "Сотрудник погиб.");
    if (showFinalResults(ackPayload.final_results || ackPayload.game_state?.final_results)) {
      return true;
    }
    if (ackPayload.game_state?.game?.started) {
      await applyGameState(ackPayload.game_state, { forceRefresh: true });
      return true;
    }
    closeGameScreen();
    closeOnlineScreen();
    closePlayScreen();
    return true;
  }
  return true;
}

async function showDeathShieldMiracleModal(damage = {}) {
  await showInfoModal(
    "Чудесное спасение",
    `Сотрудник ${discordUser?.global_name || discordUser?.username || "L"} смог пережить смертельный урон благодаря действию аномальных сил. Текущее здоровье: ${Number(damage?.hp ?? 100)}; Текущий рассудок: ${Number(damage?.sp ?? 200)}`,
    {
      iconSrc: "/photo/work_room/giveitem.png",
      iconAlt: "Чудесное спасение"
    }
  );
}

async function handleChooseBonusDeath(payload) {
  closeDetailsEventModal();
  await showDeathModal(payload.death_reason || "Сотрудник погиб.");
  if (showFinalResults(payload.final_results || payload.game_state?.final_results)) {
    return true;
  }
  if (payload.game_state?.game?.started) {
    await applyGameState(payload.game_state, { forceRefresh: true });
    return true;
  }
  try {
    const refreshedGame = await api(`/api/game?user_id=${currentUserId()}`);
    if (showFinalResults(refreshedGame?.final_results)) {
      return true;
    }
    if (refreshedGame?.game?.started) {
      await applyGameState(refreshedGame, { forceRefresh: true });
      return true;
    }
  } catch (_) {}
  closeGameScreen();
  closeOnlineScreen();
  closePlayScreen();
  return true;
}

function showChooseBonusDoorPrompt(anomalyId) {
  showDetailsChoiceModal({
    icon: "/photo/work_room/neutralresult.png",
    iconAlt: "Дверь",
    intro: "Дверь",
    effect: "Выход вон там...",
    confirmOnly: true,
    choices: []
  });
}

function renderChooseBonusModal(action, anomalyId, resultMessage = "") {
  const baseEffect = action?.effect || "Что попросить у аномалии? Не забывайте, что имеет свою цену";
  const effectText = resultMessage ? `${resultMessage}\n\n${baseEffect}` : baseEffect;
  const choiceConfig = (action?.options || []).map((option) => ({
      label: option.label,
      disabled: !!option.disabled,
      title: option.blocked_reason || "",
      onClick: async () => {
        const payload = await apiPost("/api/game/choose-bonus-apply", {
          user_id: currentUserId(),
          action_key: option.key
        });
        if (payload.details) {
          renderDetailsScreen(payload.details);
        }
        if (payload.room) {
          renderWorkRoom(payload.room);
        }
        applyDamageFeedback(payload);
        if (payload.damage?.shield_triggered) {
          await showDeathShieldMiracleModal(payload.damage);
        }
        if (payload.player_dead) {
          await handleChooseBonusDeath(payload);
          return;
        }
        if (payload.door_prompt) {
          showChooseBonusDoorPrompt(anomalyId);
          return;
        }
        renderChooseBonusModal(payload.action || action, anomalyId, payload.message || "");
      }
    }));
  showDetailsChoiceModal({
    icon: action?.icon || "/photo/work_room/neutralresult.png",
    iconAlt: action?.iconAlt || "Предложение",
    intro: action?.intro || "Предложение",
    effect: effectText,
    choices: choiceConfig
  });
}

async function openChooseBonusOffer(anomalyId, resultMessage = "") {
  const payload = await apiPost("/api/game/choose-bonus-preview", {
    user_id: currentUserId(),
    anomaly_id: anomalyId
  });
  renderChooseBonusModal(payload?.action || {}, anomalyId, resultMessage);
}

async function showContractWarningIfPending(room) {
  const warning = room?.contract_warning;
  if (!warning?.pending) return false;
  showEventChoiceModal({
    icon: warning.icon || "/photo/work_room/badresult.png",
    iconAlt: warning.iconAlt || "Предупреждение",
    intro: warning.intro || "Предупреждение!",
    effect: warning.effect || "",
    choices: [
      {
        label: "Да (-500 СО)",
        disabled: !warning.can_pay,
        title: warning.can_pay ? "" : "Недостаточно СО для откупа.",
        onSelect: async () => {
          const payload = await apiPost("/api/game/contract-respond", {
            user_id: currentUserId(),
            pay: true
          });
          closeEventModal();
          if (payload.room) {
            renderWorkRoom(payload.room);
          }
        }
      },
      {
        label: "Нет",
        onSelect: async () => {
          const payload = await apiPost("/api/game/contract-respond", {
            user_id: currentUserId(),
            pay: false
          });
          closeEventModal();
          if (payload.room) {
            renderWorkRoom(payload.room);
          }
        }
      }
    ]
  });
  return true;
}

async function showContractSummaryIfPending(source) {
  const summary = source?.contract_summary || source;
  if (!summary?.pending) return false;
  if (contractSummaryShowing) return true;
  contractSummaryShowing = true;
  try {
    await showInfoModal(summary.intro || "Исход", summary.effect || "", {
      iconSrc: summary.icon || "/photo/work_room/badresult.png",
      iconAlt: summary.iconAlt || "Исход"
    });
    const payload = await apiPost("/api/game/contract-summary-ack", {
      user_id: currentUserId(),
      anomaly_id: source?.anomaly_id || activeRoomAnomalyId
    });
    if (payload.room) renderWorkRoom(payload.room);
    if (payload.player_dead) {
      await showDeathModal(payload.death_reason || "Сотрудник погиб.");
      if (showFinalResults(payload.final_results || payload.game_state?.final_results)) return true;
      if (payload.game_state?.game?.started) {
        await applyGameState(payload.game_state, { forceRefresh: true });
        return true;
      }
      try {
        const refreshedGame = await api(`/api/game?user_id=${currentUserId()}`);
        if (showFinalResults(refreshedGame?.final_results)) return true;
        if (refreshedGame?.game?.started) {
          await applyGameState(refreshedGame, { forceRefresh: true });
          return true;
        }
      } catch (_) {}
      closeGameScreen();
    }
    return true;
  } finally {
    contractSummaryShowing = false;
  }
}

function showPsychosisModal(psychosis) {
  if (!eventOverlay) return Promise.resolve();
  const finalName = psychosis?.name || "Психоз";
  const introText = "Ваш рассудок достиг низкого уровня. Это привело к проявлению...";
  eventIcon.classList.remove("hidden");
  const rollerNames = [
    ...PSYCHOSIS_ROLLER_NAMES,
    ...PSYCHOSIS_ROLLER_NAMES,
    ...PSYCHOSIS_ROLLER_NAMES,
    finalName
  ];
  eventIcon.src = "/photo/work_room/stress.png";
  eventIcon.alt = "Психоз";
  eventIntro.textContent = introText;
  eventEffect.textContent = "";
  eventRollerWrap.classList.remove("hidden");
  eventConfirmButton.classList.add("hidden");
  eventRoller.innerHTML = rollerNames.map((name) => `<div class="event-roller-item">${name}</div>`).join("");
  eventRoller.style.transition = "none";
  eventRoller.style.transform = "translateY(0)";
  eventOverlay.classList.remove("hidden");
  return new Promise((resolve) => {
    eventModalResolver = resolve;
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        const firstItem = eventRoller.querySelector(".event-roller-item");
        const itemHeight = firstItem ? firstItem.getBoundingClientRect().height : 62.4;
        const targetIndex = rollerNames.length - 1;
        eventRoller.style.transition = "transform 3s cubic-bezier(0.16, 0.84, 0.24, 1)";
        eventRoller.style.transform = `translateY(-${itemHeight * targetIndex}px)`;
      });
    });
    window.setTimeout(() => {
      eventEffect.textContent = psychosis?.desc || "";
      eventConfirmButton.classList.remove("hidden");
    }, 3050);
  });
}

async function handleMentalEvents(payload) {
  if (payload?.psychosis) {
    await enqueueSystemEventModal(() => showPsychosisModal(payload.psychosis));
  }
  if (payload?.heart_attack?.triggered && !payload?.heart_attack?.dead) {
    await enqueueSystemEventModal(() => showHeartAttackModal());
  }
}

function getDeathReasonFromPayload(payload) {
  return payload?.room?.player_stats?.death_reason
    || payload?.death_reason
    || payload?.heart_attack?.message
    || "Причина смерти неизвестна.";
}

function playSound(name) {
  const audio = soundPlayers[name];
  if (!audio) return;
  try {
    audio.currentTime = 0;
    audio.play().catch(() => {});
  } catch (_) {}
}

function triggerDamageFlash() {
  if (!gameDamageFlash) return;
  gameDamageFlash.classList.remove("active");
  void gameDamageFlash.offsetWidth;
  gameDamageFlash.classList.add("active");
  window.setTimeout(() => {
    gameDamageFlash.classList.remove("active");
  }, 700);
}

function hasDamageFeedback(payload = {}) {
  const damage = payload?.damage || {};
  return Number(damage?.hp_damage_final || damage?.hp_damage || 0) > 0
    || Number(damage?.sp_damage_final || damage?.sp_damage || 0) > 0;
}

function applyDamageFeedback(payload = {}) {
  if (!hasDamageFeedback(payload)) return;
  playSound("damageHit");
  triggerDamageFlash();
}

function clearDetails() {
  codexDetails.classList.add("empty");
  codexDetails.innerHTML = "";
}

function updateProfile(user) {
  discordUser = user || null;
  profileMenu.classList.add("hidden");
  if (!discordUser) {
    profileAvatar.classList.add("hidden");
    profileAvatar.removeAttribute("src");
    profilePlaceholder.classList.remove("hidden");
    profilePlaceholder.textContent = "войти";
    profileUsername.textContent = "";
    profileGlobalName.textContent = "";
    profileLogout.classList.add("hidden");
    return;
  }

  profileAvatar.src = discordUser.avatar_url || "/photo/web_ui/nophoto.png";
  profileAvatar.classList.remove("hidden");
  profilePlaceholder.classList.add("hidden");
  profileUsername.textContent = discordUser.username || "Discord";
  profileGlobalName.textContent = discordUser.global_name || discordUser.id || "";
  profileLogout.classList.toggle("hidden", !!discordUser.isFallback);
}

function clearAndHide(screen) {
  screen.classList.add("hidden");
}

async function openPlayScreen() {
  if (!discordUser?.id) {
    const useDiscord = discordOauthEnabled && window.confirm(
      "Войти через Discord?\n\nОК — Discord\nОтмена — гостевой режим"
    );
    if (useDiscord) {
      window.location.href = "/auth/discord/login";
      return;
    }
    const guest = await apiPost("/api/auth/guest", {});
    updateProfile(guest.user || null);
  }
  playScreen.classList.remove("hidden");
  toast.classList.remove("visible");
}

function closePlayScreen() {
  clearAndHide(playScreen);
}

function currentUserPayload() {
  return {
    // Discord snowflakes exceed JavaScript's safe integer range.
    user_id: String(discordUser?.id || ""),
    username: discordUser?.global_name || discordUser?.username || "Игрок",
    avatar_url: discordUser?.avatar_url || null
  };
}

function currentUserId() {
  return String(discordUser?.id || "");
}

function sameUserId(left, right) {
  return String(left ?? "") === String(right ?? "");
}

function stopOnlinePolling() {
  if (onlineLobbyPoller) {
    window.clearInterval(onlineLobbyPoller);
    onlineLobbyPoller = null;
  }
}

function stopGamePolling() {
  if (gameStatePoller) {
    window.clearInterval(gameStatePoller);
    gameStatePoller = null;
  }
  gameStatePollBusy = false;
}

function openOnlineListView() {
  onlineListView.classList.remove("hidden");
  onlineRoomView.classList.add("hidden");
}

function openOnlineRoomView() {
  onlineListView.classList.add("hidden");
  onlineRoomView.classList.remove("hidden");
}

function playerAvatarMarkup(player) {
  if (player.avatar_url) {
    return `<img class="online-player-avatar" src="${player.avatar_url}" alt="${player.name}">`;
  }
  const initial = (player.name || "?").trim().charAt(0).toUpperCase() || "?";
  return `<div class="online-player-avatar placeholder">${initial}</div>`;
}

function lobbyPreviewAvatars(players = []) {
  if (!players.length) return `<div class="online-lobby-preview-empty">пусто</div>`;
  return `
    <div class="online-lobby-preview">
      ${players.slice(0, 4).map((player) => `
        <div class="online-lobby-preview-avatar" title="${player.name}">
          ${player.avatar_url ? `<img src="${player.avatar_url}" alt="${player.name}">` : `<span>${(player.name || "?").trim().charAt(0).toUpperCase() || "?"}</span>`}
        </div>
      `).join("")}
    </div>
  `;
}

function renderLobbyList(lobby) {
  const count = lobby.players?.length || 0;
  if (lobby.exists) {
    onlineLobbyList.innerHTML = `
      <article class="online-lobby-card">
        <div class="online-lobby-meta">
          <div class="online-lobby-name">Активное лобби</div>
          <div class="online-lobby-sub">${count} / ${lobby.capacity} игроков</div>
          ${lobbyPreviewAvatars(lobby.players || [])}
        </div>
        <button class="online-action-button" id="joinLobbyButton" type="button">Открыть</button>
      </article>
    `;
    const joinButton = document.getElementById("joinLobbyButton");
    if (joinButton) joinButton.addEventListener("click", () => {
      openOnlineRoomView();
      renderLobbyRoom(lobby);
    });
    createLobbyButton.disabled = true;
  } else {
    onlineLobbyList.innerHTML = `<div class="online-empty-card">Активных лобби нет</div>`;
    createLobbyButton.disabled = false;
  }
}

function renderObserverCard() {
  const lobbyPlayers = Array.from(onlinePlayerGrid?.querySelectorAll?.("[data-player-id]") || []);
  const inSlot = lobbyPlayers.some((card) => sameUserId(card.dataset.playerId, currentUserId()));
  if (inSlot) {
    onlineObserverCard.innerHTML = `
      <div class="online-observer-role compact">Ты в игровом слоте</div>
    `;
    return;
  }
  const observer = {
    name: discordUser?.global_name || discordUser?.username || "Наблюдатель",
    avatar_url: discordUser?.avatar_url || null
  };
  onlineObserverCard.innerHTML = `
    <div class="online-observer-avatar-wrap">
      ${playerAvatarMarkup(observer)}
    </div>
    <div class="online-observer-name" title="${observer.name}">${observer.name}</div>
    <div class="online-observer-role">наблюдатель</div>
  `;
}

async function changeOwnArtifact(direction) {
  const payload = await apiPost("/api/lobby/artifact", { user_id: currentUserId(), direction });
  renderLobbyRoom(payload.lobby || payload);
}

async function setOwnReady(ready) {
  const lobby = await apiPost("/api/lobby/ready", { user_id: currentUserId(), ready });
  renderLobbyRoom(lobby);
}

async function leaveOwnSlot() {
  const lobby = await apiPost("/api/lobby/leave", { user_id: currentUserId() });
  renderLobbyRoom(lobby);
}

function renderRoomBanner(lobby) {
  if (lobby.status === "countdown" && lobby.countdown_started_at) {
    const startedAt = Number(lobby.countdown_started_at) * 1000;
    const remaining = Math.max(0, Math.ceil((startedAt + 5000 - Date.now()) / 1000));
    onlineRoomBanner.textContent = remaining > 0 ? `Игра начнется через ${remaining} сек.` : "Запуск игры...";
    onlineRoomBanner.classList.remove("hidden");
    onlineRoomBanner.classList.remove("started");
    return;
  }
  if (lobby.status === "started") {
    onlineRoomBanner.textContent = "Игра началась";
    onlineRoomBanner.classList.remove("hidden");
    onlineRoomBanner.classList.add("started");
    return;
  }
  onlineRoomBanner.classList.add("hidden");
  onlineRoomBanner.classList.remove("started");
  onlineRoomBanner.textContent = "";
}

function renderLobbyRoom(lobby) {
  const players = lobby.players || [];
  const me = currentUserId();
  const mySlotIndex = players.findIndex((player) => sameUserId(player.id, me));
  onlineRoomCount.textContent = `${players.length} / ${lobby.capacity}`;
  renderRoomBanner(lobby);
  const cards = [];
  for (let i = 0; i < lobby.capacity; i += 1) {
    const player = players[i];
    if (player) {
      const isMe = sameUserId(player.id, me);
      const artName = player.art_name || "Не выбран";
      const artDescription = player.art_description || "Описание эффекта пока отсутствует.";
      const readyText = player.ready ? "Готов" : "Не готов";
      cards.push(`
        <article class="online-player-card ${isMe ? "is-self" : ""}" data-player-id="${player.id}">
          ${playerAvatarMarkup(player)}
          <div class="online-player-name" title="${player.name}">${player.name}</div>
          <div class="online-player-status ${player.ready ? "ready" : "not-ready"}">
            <span class="ready-indicator ${player.ready ? "ready" : "not-ready"}">${player.ready ? "✓" : "✕"}</span>
            <span>${readyText}</span>
          </div>
          <div class="online-artifact-block">
            ${isMe ? `<button class="artifact-arrow" type="button" data-artifact-direction="left" aria-label="Предыдущий артефакт">&#x2039;</button>` : `<span class="artifact-arrow ghost">&#x2039;</span>`}
            <div class="online-artifact-copy">
              <div class="online-artifact-label">Артефакт:</div>
              <div class="online-artifact-name" title="${artDescription}">${artName}</div>
            </div>
            ${isMe ? `<button class="artifact-arrow" type="button" data-artifact-direction="right" aria-label="Следующий артефакт">&#x203A;</button>` : `<span class="artifact-arrow ghost">&#x203A;</span>`}
          </div>
          ${isMe ? `<div class="slot-actions"><button class="ready-toggle ${player.ready ? "is-ready" : "is-not-ready"}" type="button" data-ready-toggle="${player.ready ? "off" : "on"}"><span class="ready-toggle-icon">${player.ready ? "✓" : "✕"}</span><span>${player.ready ? "Готов" : "Не готов"}</span></button><button class="slot-leave-button" type="button" data-leave-slot="true">В наблюдатели</button></div>` : ``}
        </article>
      `);
      continue;
    }
    cards.push(`
      <article class="online-player-slot ${mySlotIndex === -1 ? "joinable" : ""}" ${mySlotIndex === -1 ? `data-join-slot="${i + 1}"` : ""}>
        <div class="online-player-avatar placeholder">+</div>
        <div class="online-player-name">Свободный слот</div>
        <div class="online-player-status">${mySlotIndex === -1 ? "Нажми, чтобы зайти" : "Ожидание игрока"}</div>
      </article>
    `);
  }
  onlinePlayerGrid.innerHTML = cards.join("");
  renderObserverCard();
  onlinePlayerGrid.querySelectorAll("[data-join-slot]").forEach((slot) => {
    slot.addEventListener("click", () => joinLobby().catch((error) => showRuntimeErrorModal(error)));
  });
  onlinePlayerGrid.querySelectorAll("[data-artifact-direction]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      changeOwnArtifact(button.dataset.artifactDirection).catch((error) => showRuntimeErrorModal(error));
    });
  });
  onlinePlayerGrid.querySelectorAll("[data-ready-toggle]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      setOwnReady(button.dataset.readyToggle === "on").catch((error) => showRuntimeErrorModal(error));
    });
  });
  onlinePlayerGrid.querySelectorAll("[data-leave-slot]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      leaveOwnSlot().catch((error) => showRuntimeErrorModal(error));
    });
  });
}

async function loadOnlineLobby() {
  const lobby = await api("/api/lobby");
  renderLobbyList(lobby);
  if (!onlineRoomView.classList.contains("hidden")) renderLobbyRoom(lobby);
  if (lobby.status === "started") openGameSequence().catch(() => {});
  return lobby;
}

async function joinLobby() {
  const lobby = await apiPost("/api/lobby/join", currentUserPayload());
  openOnlineRoomView();
  renderLobbyRoom(lobby);
}

async function createLobby() {
  const lobby = await apiPost("/api/lobby/create", {});
  openOnlineRoomView();
  renderLobbyRoom(lobby);
}

async function openOnlineScreen() {
  playScreen.classList.add("hidden");
  onlineScreen.classList.remove("hidden");
  openOnlineListView();
  await loadOnlineLobby();
  stopOnlinePolling();
  onlineLobbyPoller = window.setInterval(() => {
    loadOnlineLobby().catch(() => {});
  }, 1000);
}

function closeOnlineScreen() {
  stopOnlinePolling();
  clearAndHide(onlineScreen);
  openOnlineListView();
}

function closeGameScreen() {
  stopGamePolling();
  stopGameMusic();
  finishPreviewActive = false;
  upgradeModalBusy = false;
  lastFinishReward = { cp: 0, rt: 0 };
  closeEventModal();
  closeStatUpgradeModal();
  gameSelectScreen.classList.add("hidden");
  gameRoomScreen.classList.add("hidden");
  gameDetailsScreen.classList.add("hidden");
  gameDayOverlay.classList.add("hidden");
  gameDayOverlay.classList.remove("transition");
  gameFinalScreen.classList.add("hidden");
  gameWaitingScreen.classList.add("hidden");
  gameScreen.classList.add("hidden");
  completionAlertPlayed = false;
}

function finalAvatarMarkup(entry) {
  if (entry?.avatar_url) {
    return `<img src="${entry.avatar_url}" alt="${entry.name || "Игрок"}">`;
  }
  return `<span>${((entry?.name || "?").trim().charAt(0).toUpperCase() || "?")}</span>`;
}

function showFinalResults(finalResults = {}) {
  if (deferFinalResultsModal) return false;
  const standings = Array.isArray(finalResults.standings) ? finalResults.standings : [];
  if (!standings.length) return false;
  stopSpectatorCamera();
  gameScreen.classList.remove("hidden");
  gameDayOverlay.classList.add("hidden");
  gameWaitingScreen.classList.add("hidden");
  gameSelectScreen.classList.add("hidden");
  gameRoomScreen.classList.add("hidden");
  gameDetailsScreen.classList.add("hidden");
  gameFinalWinner.textContent = `Победитель: ${finalResults.winner_name || "-"}`;
  gameFinalList.innerHTML = standings.map((entry, index) => `
    <article class="game-final-row">
      <div class="game-final-rank">${index + 1}.</div>
      <div class="game-final-avatar">${finalAvatarMarkup(entry)}</div>
      <div class="game-final-copy">
        <div class="game-final-name ${entry.is_dead ? "dead" : ""}">${entry.name}${entry.is_dead ? " [МЁРТВ]" : ""}</div>
        ${entry.is_dead && entry.death_reason ? `<div class="game-final-death-reason">${entry.death_reason}</div>` : ""}
      </div>
      <div class="game-final-cp">${Number(entry.cp || 0).toLocaleString("ru-RU")} CP</div>
    </article>
  `).join("");
  gameFinalScreen.classList.remove("hidden");
  return true;
}

function avatarChip(player, extraClass = "") {
  if (player?.avatar_url) {
    return `<img class="game-turn-avatar ${extraClass}" src="${player.avatar_url}" alt="${player?.name || "Игрок"}">`;
  }
  const initial = (player?.name || "?").trim().charAt(0).toUpperCase() || "?";
  return `<div class="game-turn-avatar placeholder ${extraClass}">${initial}</div>`;
}

function renderTurnRibbon(turnUi = {}) {
  if (!gameTurnTrack) return;
  const players = Array.isArray(turnUi.players) ? turnUi.players : [];
  const alivePlayers = players.filter((player) => player.alive !== false);
  const currentPlayer = players.find((player) => player.is_current) || null;
  const futureDays = Array.isArray(turnUi.future_days) ? turnUi.future_days : [];
  const currentDay = Number(turnUi.current_day || 0);

  const currentDayCard = `
    <section class="game-turn-current-day">
      <div class="game-turn-current-day-label">День ${currentDay || 1}</div>
      <div class="game-turn-current-players">
        ${alivePlayers.map((player) => `
          <article class="game-turn-player ${player.is_current ? "is-current" : ""}">
            ${avatarChip(player)}
            <div class="game-turn-player-name">${player.is_current ? (player.name || "Игрок") : ""}</div>
          </article>
        `).join("")}
      </div>
    </section>
  `;

  const futureMarkup = futureDays.map((day) => `
    <section class="game-turn-future-day">
      <div class="game-turn-future-circle">${day.day}</div>
      <div class="game-turn-future-players">
        ${(day.players || []).map((player) => avatarChip(player, "small")).join("")}
      </div>
    </section>
  `).join("");

  gameTurnTrack.innerHTML = currentDayCard + futureMarkup;
  gameWaitingTitle.textContent = turnUi.is_alive === false ? "Вы мертвы" : "Ожидание хода";
  if (currentPlayer?.id && !sameUserId(currentPlayer.id, currentUserId())) {
    gameWaitingSubtitle.textContent = `Сейчас ходит ${currentPlayer.name || "другой игрок"}.`;
  } else if (turnUi.is_alive === false) {
    gameWaitingSubtitle.textContent = "Игра продолжается, пока жив хотя бы один сотрудник.";
  } else {
    gameWaitingSubtitle.textContent = "Ожидание следующего этапа игры.";
  }
}

function resetRoomResultGrid() {
  clearTimeout(roomResultTimer);
  gameRoomResultGrid.innerHTML = Array.from({ length: 10 }, (_, index) => `
    <div class="game-room-slot ${index < 5 ? "fail-lane" : "success-lane"}">
      <div class="game-room-slot-fill"></div>
    </div>
  `).join("");
  gameRoomResultScore.textContent = "";
  gameRoomResultScore.classList.remove("positive");
  gameRoomResultScore.classList.add("hidden-score");
}

function renderRoomResult(rolls = [], finalRp = null) {
  resetRoomResultGrid();
  const slots = Array.from(gameRoomResultGrid.querySelectorAll(".game-room-slot"));
  const successes = rolls.filter((value) => value === 1).length;
  const failures = Math.max(0, 10 - successes);
  const revealTypes = Array.from({ length: failures }, () => "fail").concat(
    Array.from({ length: successes }, () => "success")
  );
  for (let i = revealTypes.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [revealTypes[i], revealTypes[j]] = [revealTypes[j], revealTypes[i]];
  }
  let failSlotIndex = 0;
  let successSlotIndex = 9;
  revealTypes.forEach((fillType, index) => {
    window.setTimeout(() => {
      const slotIndex = fillType === "fail" ? failSlotIndex++ : successSlotIndex--;
      const slot = slots[slotIndex];
      if (!slot) return;
      slot.classList.add(fillType === "success" ? "filled-success" : "filled-fail");
      slot.querySelector(".game-room-slot-fill").innerHTML = `<img src="${fillType === "success" ? "/photo/work_room/success.png" : "/photo/work_room/fail.png"}" alt="">`;
    }, index * 140);
  });
  roomResultTimer = window.setTimeout(() => {
    gameRoomResultScore.textContent = `+${successes}`;
    gameRoomResultScore.classList.toggle("positive", successes > 0);
    gameRoomResultScore.classList.remove("hidden-score");
    if (finalRp !== null && finalRp !== undefined) {
      gameRoomRpValue.textContent = String(finalRp);
    }
  }, revealTypes.length * 140 + 120);
}

function renderHiddenRoomResult() {
  resetRoomResultGrid();
  const slots = Array.from(gameRoomResultGrid.querySelectorAll(".game-room-slot"));
  slots.forEach((slot, index) => {
    window.setTimeout(() => {
      slot.classList.add("filled-unknown");
      slot.querySelector(".game-room-slot-fill").textContent = "?";
    }, index * 140);
  });
  roomResultTimer = window.setTimeout(() => {
    gameRoomResultScore.textContent = "НЕИЗВЕСТНО";
    gameRoomResultScore.classList.remove("positive", "hidden-score");
    gameRoomRpValue.textContent = "?";
  }, slots.length * 140 + 120);
}

function workButtonMap() {
  return {
    intuition: workButtonIntuition,
    insight: workButtonInsight,
    affection: workButtonAffection,
    suppression: workButtonSuppression
  };
}

function resetAnomalyCustomButtons() {
  anomalyCustomButtonDefaults.forEach((defaults, buttonId) => {
    const button = document.getElementById(buttonId);
    if (!button) return;
    button.innerHTML = defaults.html;
    button.classList.remove("has-custom-art", "has-custom-wide-art");
    button.dataset.placeholderButton = "false";
    button.dataset.blocked = "false";
    button.disabled = false;
    button.classList.remove("disabled");
    if (defaults.ariaLabel) {
      button.setAttribute("aria-label", defaults.ariaLabel);
    } else {
      button.removeAttribute("aria-label");
    }
    if (defaults.title) {
      button.setAttribute("title", defaults.title);
    } else {
      button.removeAttribute("title");
    }
  });
}

function setAnomalyCustomButton(button, config, type = "work") {
  if (!button || !config?.image) return;
  button.classList.add("has-custom-art");
  button.dataset.placeholderButton = "true";
  if (type === "action") {
    button.classList.add("has-custom-wide-art");
  }
  button.innerHTML = [
    `<img class="${type === "action" ? "game-room-action-custom-icon" : "game-room-work-icon game-room-work-icon-custom"}" src="${config.image}" alt="">`,
    config.label ? `<span class="${type === "action" ? "game-room-action-custom-label" : "game-room-work-label"}">${config.label}</span>` : "",
    config.label ? `<span class="sr-only">${config.label}</span>` : ""
  ].join("");
  if (config.label) {
    button.setAttribute("aria-label", config.label);
  }
}

function applyAnomalyCustomButtons(room) {
  resetAnomalyCustomButtons();
  const config = ANOMALY_CUSTOM_BUTTONS[Number(room?.anomaly_id) || 0];
  if (!config) return;

  const workButtons = workButtonMap();
  Object.entries(config.work || {}).forEach(([key, buttonConfig]) => {
    setAnomalyCustomButton(workButtons[key], buttonConfig, "work");
  });
  if (Number(room?.anomaly_id) === 11) {
    const resetButton = workButtons.suppression;
    const available = !!room?.special_actions?.reset?.available;
    if (resetButton) {
      resetButton.dataset.placeholderButton = "false";
      resetButton.dataset.blocked = available ? "false" : "true";
      resetButton.disabled = !available;
      resetButton.classList.toggle("disabled", !available);
      resetButton.title = available ? "" : "Сброс уже был произведен";
    }
  }
  if (Number(room?.anomaly_id) === 63) {
    Object.entries(workButtons).forEach(([key, button]) => {
      if (!button) return;
      const allowed = key === "intuition";
      button.dataset.placeholderButton = "false";
      button.dataset.blocked = allowed ? "false" : "true";
      button.disabled = !allowed;
      button.classList.toggle("disabled", !allowed);
      button.title = allowed ? "" : "Сейчас доступна только сделка.";
    });
  }
  if (Number(room?.anomaly_id) === 68) {
    const donateButton = workButtons.insight;
    const available = !!room?.special_actions?.anomaly68_donation?.available;
    if (donateButton) {
      donateButton.dataset.placeholderButton = "false";
      donateButton.dataset.blocked = available ? "false" : "true";
      donateButton.disabled = !available;
      donateButton.classList.toggle("disabled", !available);
      donateButton.title = available ? "Передать первый доступный предмет" : "Предмет уже передан";
    }
  }
  if (Number(room?.anomaly_id) === 133) {
    const sacrificeButton = workButtons.intuition;
    if (sacrificeButton) {
      // This custom button is an interactive action, not a decorative placeholder.
      sacrificeButton.dataset.placeholderButton = "false";
      sacrificeButton.dataset.blocked = "false";
      sacrificeButton.disabled = false;
      sacrificeButton.classList.remove("disabled");
      sacrificeButton.title = "Пожертвовать HP механизму";
    }
  }
}

function setWorkButtonsDisabled(disabled) {
  Object.values(workButtonMap()).forEach((button) => {
    const blocked = button.dataset.blocked === "true";
    button.disabled = disabled || blocked;
    button.classList.toggle("disabled", disabled || blocked);
  });
}

function setResearchLockedState(locked, reason = "") {
  [
    actionWorkButton,
    actionFinishButton,
    actionArtifactButton,
    actionViolinButton
  ].forEach((button) => {
    if (!button) return;
    button.disabled = !!locked;
    button.classList.toggle("disabled", !!locked);
    button.title = locked ? (reason || "Действие временно недоступно.") : "";
  });
  [actionInventoryButton, actionFleeButton].forEach((button) => {
    if (!button) return;
    button.disabled = false;
    button.classList.remove("disabled");
    button.title = "";
  });
}

function applyAnomalyActionLock(room) {
  const alastorOnlyWork = Number(room?.anomaly_id) === 63;
  const alastorAccepted = alastorOnlyWork && !!room?.alastor_deal?.accepted;
  const predatorResolved = Number(room?.anomaly_id) === PREDATOR_ANOMALY_ID && !!room?.predator_vn_resolved;
  const curse137Pending = Number(room?.anomaly_id) === 137 && !!room?.curse137_pending;
  [actionInventoryButton, actionFleeButton, actionArtifactButton, actionViolinButton].forEach((button) => {
    if (!button) return;
    const disabled = alastorOnlyWork || (predatorResolved && button !== actionFleeButton) || (curse137Pending && button === actionFleeButton);
    button.disabled = disabled;
    button.classList.toggle("disabled", disabled);
    button.title = disabled ? (curse137Pending && button === actionFleeButton
      ? "Сначала завершите создание проклятия."
      : (alastorOnlyWork ? "Сейчас доступна только сделка." : "VN-сценарий завершён.")) : "";
  });
  if (actionFinishButton) {
    const finishLocked = alastorOnlyWork && !alastorAccepted;
    actionFinishButton.disabled = finishLocked;
    actionFinishButton.classList.toggle("disabled", finishLocked);
    actionFinishButton.title = finishLocked ? "Сейчас доступна только сделка." : "";
  }
  if (actionWorkButton) {
    actionWorkButton.disabled = predatorResolved;
    actionWorkButton.classList.toggle("disabled", predatorResolved);
    actionWorkButton.title = predatorResolved ? "VN-сценарий завершён." : "";
  }
}

function renderWorkHints(works = []) {
  gameRoomWorkMeta.textContent = "";
}

function workLabel(workType) {
  return {
    intuition: "Интуиция",
    insight: "Понимание",
    affection: "Привязанность",
    suppression: "Подавление"
  }[workType] || workType || "Не выбрано";
}

function renderWorkDebug(debugInfo = null) {
  if (!gameRoomDebug || !debugModeEnabled) return;
  if (!debugInfo) {
    gameRoomDebug.textContent = [
      "DEBUG",
      "Стат: -",
      "Работа: -",
      "База: -",
      "Мод. класса: -",
      "Мод. типа: -",
      "Итог: -"
    ].join("\n");
    return;
  }
  gameRoomDebug.textContent = [
    "DEBUG",
    `Стат: ${debugInfo.stat_column || "-"} = ${debugInfo.stat_value ?? "-"}`,
    `Работа: ${workLabel(debugInfo.work_type)}`,
    `База: ${debugInfo.base_column || "-"} = ${debugInfo.base_chance ?? "-"}`,
    `Мод. класса: ${debugInfo.class_modifier ?? 0}`,
    `Мод. типа: ${debugInfo.type_modifier ?? 0}`,
    `Мод. компаньона: ${debugInfo.companion_modifier ?? 0}`,
    `Итог: ${debugInfo.final_chance ?? "-"}`
  ].join("\n");
}

function renderGlobalDebug(globalsList = []) {
  if (!gameRoomGlobals || !debugModeEnabled) return;
  if (!Array.isArray(globalsList) || !globalsList.length) {
    gameRoomGlobals.textContent = [
      "GLOBALS",
      "-"
    ].join("\n");
    return;
  }
  gameRoomGlobals.textContent = [
    "GLOBALS",
    ...globalsList.map((item) => `${item.key || "-"} = ${item.value ?? "-"}`)
  ].join("\n");
}

function renderAdminStats(stats = null) {
  if (!gameRoomAdminStats || !debugModeEnabled) return;
  if (!stats) {
    gameRoomAdminStats.innerHTML = [
      "HP: -   SP: -",
      "RP: -   RT: -   CP: -",
      "BONUS: -   PENALTY: -",
      "COMPSLOT: -",
      "STAT1: -  STAT2: -",
      "STAT3: -  STAT4: -",
      "Психоз: -",
      "Эффекты: -",
    ].join("<br>");
    return;
  }
  const effects = Array.isArray(stats.effects) ? stats.effects : [];
  const companion = stats.companion || null;
  const companionHp = Number.isFinite(Number(companion?.hp)) ? ` (${Number(companion.hp)} HP)` : "";
  const companionHtml = companion
    ? `<span class="admin-companion-chip" title="${escapeHtml(companion.description || "Описание компаньона пока не добавлено.")}">#${Number(companion.id || 0)} ${escapeHtml(companion.name || "Компаньон")}${escapeHtml(companionHp)}</span>`
    : `<span class="admin-companion-empty">-</span>`;
  const effectsHtml = effects.length
    ? effects.map((effect) => {
        const rawValue = effect.raw || effect.key || "";
        const nameValue = effect.name || effect.key || rawValue || "Неизвестный эффект";
        const name = escapeHtml(nameValue);
        const desc = escapeHtml(effect.description || "Описание эффекта пока не добавлено.");
        return `<span class="admin-effect-chip" title="${desc}"><span class="admin-effect-name">${name}</span></span>`;
      }).join("")
    : `<span class="admin-effect-empty">-</span>`;
  gameRoomAdminStats.innerHTML = [
    `HP: ${stats.hp ?? 0}   SP: ${stats.sp ?? 0}`,
    `RP: ${stats.rp ?? 0}   RT: ${stats.rt ?? 0}   CP: ${stats.cp ?? 0}`,
    `BONUS: ${stats.bonus ?? 0}   PENALTY: ${stats.penalty ?? 0}`,
    `COMPSLOT: <span class="admin-companion-line">${companionHtml}</span>`,
    `STAT1: ${stats.stat1 ?? 1}  STAT2: ${stats.stat2 ?? 1}`,
    `STAT3: ${stats.stat3 ?? 1}  STAT4: ${stats.stat4 ?? 1}`,
    `Психоз: ${stats.psychosis?.name || "-"}`,
    `Эффекты:<div class="admin-effect-list">${effectsHtml}</div>`,
  ].join("<br>");
}

function renderPlayerStatus(status = null) {
  if (!gameRoomPlayerStatus) return;
  if (!status) {
    gameRoomPlayerStatus.innerHTML = "Состояние недоступно";
    return;
  }
  const snapshotHint = "Здоровье отображается на момент взятия аномалии. Информация обновится после завершения работы";
  const stats = Array.isArray(status.stats) ? status.stats : [];
  const effects = Array.isArray(status.effects) ? status.effects : [];
  const psychosis = status.psychosis?.name || "-";
  const companionHp = Number.isFinite(Number(status.companion?.hp)) ? ` (${Number(status.companion.hp)} HP)` : "";
  const companion = status.companion?.name ? `${status.companion.name}${companionHp}` : "-";
  const companionDescription = status.companion?.description || "Описание компаньона пока не добавлено.";
  const companionMarkup = status.companion?.name
    ? `<span class="player-status-companion" tabindex="0" title="${escapeHtml(companionDescription)}" data-tooltip="${escapeHtml(companionDescription)}">${escapeHtml(companion)}</span>`
    : "-";
  const statMarkup = stats.map((stat) => `
    <div class="player-status-stat" title="${escapeHtml(stat.name || "Характеристика")}">
      <img src="${escapeHtml(stat.icon || "")}" alt="${escapeHtml(stat.name || "Характеристика")}">
      <span>${Number(stat.value || 0)}</span>
    </div>
  `).join("");
  const effectMarkup = effects.length
    ? effects.map((effect) => `<span class="player-status-effect" title="${escapeHtml(effect.description || "")}">${escapeHtml(effect.name || effect.key || "Неизвестный эффект")}</span>`).join("")
    : "-";
  gameRoomPlayerStatus.innerHTML = `
    <div class="player-status-line">ХП ${Number(status.hp || 0)}/${Number(status.max_hp || 0)} <span class="player-status-help" title="${snapshotHint}">?</span></div>
    <div class="player-status-line">SP ${Number(status.sp || 0)}/${Number(status.max_sp || 0)} <span class="player-status-help" title="${snapshotHint}">?</span></div>
    <div class="player-status-line">Бонус: ${Number(status.bonus || 0)}%</div>
    <div class="player-status-line">Клипота: ${Number(status.klipota || 0)}</div>
    <div class="player-status-line">СО: ${Number(status.cp || 0)}</div>
    <div class="player-status-caption">Характеристики (RT: ${Number(status.rt || 0)})</div>
    <div class="player-status-stats">${statMarkup || "-"}</div>
    <div class="player-status-line">Психоз: ${escapeHtml(psychosis)}</div>
    <div class="player-status-line player-status-effects">Эффекты: <span>${effectMarkup}</span></div>
    <div class="player-status-line">Компаньон: ${companionMarkup}</div>
  `;
}

async function adminAction(action, value = null) {
  if (!debugModeEnabled) throw new Error("Режим отладки отключён.");
  const payload = await apiPost("/api/admin/action", {
    user_id: currentUserId(),
    action,
    value
  });
  if (payload.message) {
    showInfoToast(payload.message);
  }
  if (payload.x125_event) {
    await handleX125Events([payload.x125_event]);
  }
  if (payload.x125_special_event) {
    await handleX125SpecialEvent(payload.x125_special_event);
  }
  if (payload.room?.player_stats?.is_dead) {
    await handleMentalEvents(payload);
    await showDeathModal(getDeathReasonFromPayload(payload));
    if (showFinalResults(payload.game_state?.final_results)) {
      return;
    }
    closeGameScreen();
    closeOnlineScreen();
    closePlayScreen();
    return;
  }
  if (payload.room) {
    renderWorkRoom(payload.room);
    const initialEffectAnimation = payload.initial_effect_result ? playInitialEffectAnimation() : Promise.resolve();
    if (payload.initial_effect_result?.description) {
      showInfoToast(payload.initial_effect_result.description);
    }
    await initialEffectAnimation;
    if (payload.initial_effect_result?.event) {
      const handled = await handleQueuedUiEvent(payload.initial_effect_result, null);
      if (handled) {
        return;
      }
    }
    await handleMentalEvents(payload);
    return;
  }
  if (activeRoomAnomalyId) {
    const roomPayload = await api(`/api/work-room?user_id=${currentUserId()}&anomaly_id=${activeRoomAnomalyId}`);
    renderWorkRoom(roomPayload.room);
  } else if (payload.game_state?.game?.started) {
    await applyGameState(payload.game_state, { forceRefresh: true });
  }
}

function detailsHintCost(index) {
  return 6 + (2 * Math.max(0, index - 1));
}

function renderDetailsBase(details) {
  const base = details.base_info || {};
  if (details.base_unlocked) {
    gameDetailsBaseMedia.classList.add("unlocked");
    gameDetailsBaseName.classList.remove("hidden");
    gameDetailsBaseCode.classList.remove("hidden");
    gameDetailsBaseRisk.classList.remove("hidden");
    gameDetailsDmgType.classList.remove("hidden");
    gameDetailsDmgAmount.classList.remove("hidden");
    gameDetailsGoodRange.classList.remove("hidden");
    gameDetailsBadRange.classList.remove("hidden");
    gameDetailsBaseMedia.innerHTML = `<button class="game-details-photo-button" id="gameDetailsPhotoButton" type="button" aria-label="Открыть фото"><img class="game-details-photo" src="${base.photo_url || "/photo/work_room/404.png"}" alt="${base.name || "Аномалия"}"></button>`;
    gameDetailsBaseName.textContent = base.name || "Неизвестно";
    gameDetailsBaseCode.textContent = base.code_name || String(details.anomaly_id || "");
    gameDetailsBaseRisk.textContent = base.risk_label || "UNKNOWN";
    gameDetailsBaseRisk.style.color = base.risk_color || "#f3eca9";
    const dmgIconMap = {
      RED: "/photo/work_room/dmg1.png",
      BLACK: "/photo/work_room/dmg2.png",
      MIXED: "/photo/work_room/dmg3.png",
      WHITE: "/photo/work_room/dmg4.png"
    };
    const dmgHintMap = {
      RED: "Атакует HP",
      BLACK: "Атакует SP",
      MIXED: "Бьет одновременно HP и SP",
      WHITE: "Особый тип урона"
    };
    const dmgIcon = dmgIconMap[base.dmg_type] || null;
    gameDetailsDmgAmount.classList.remove("dmg-red", "dmg-black", "dmg-mixed");
    if (base.dmg_type === "RED") gameDetailsDmgAmount.classList.add("dmg-red");
    if (base.dmg_type === "BLACK") gameDetailsDmgAmount.classList.add("dmg-black");
    if (base.dmg_type === "MIXED") gameDetailsDmgAmount.classList.add("dmg-mixed");
    gameDetailsDmgType.title = dmgHintMap[base.dmg_type] || "";
    gameDetailsDmgType.innerHTML = dmgIcon
      ? `<img class="game-details-dmg-icon" src="${dmgIcon}" alt="${base.dmg_type || "DMG"}">`
      : `<span>-</span>`;
    gameDetailsDmgAmount.textContent = base.dmg_amount || "-";
    gameDetailsGoodRange.textContent = base.good_range || "-";
    gameDetailsBadRange.textContent = base.bad_range || "-";
    const photoButton = document.getElementById("gameDetailsPhotoButton");
    if (photoButton) {
      photoButton.addEventListener("click", () => {
        gameDetailsLightboxImage.src = base.photo_url || "/photo/work_room/404.png";
        gameDetailsLightboxImage.alt = base.name || "Аномалия";
        gameDetailsLightbox.classList.remove("hidden");
      });
    }
    return;
  }
  gameDetailsBaseMedia.classList.remove("unlocked");
  gameDetailsBaseMedia.innerHTML = `
    <button class="game-details-unlock-button" id="detailsBaseUnlockButton" type="button">
      <img src="/photo/work_room/base-unlock.png" alt="Базовая информация">
      <span class="game-details-unlock-cost">${details.base_unlock_cost || 15}</span>
    </button>
  `;
  gameDetailsBaseName.textContent = "Неизвестно";
  gameDetailsBaseCode.textContent = "ID";
  gameDetailsBaseRisk.textContent = "UNKNOWN";
  gameDetailsBaseRisk.style.color = "#f3eca9";
  gameDetailsDmgAmount.classList.remove("dmg-red", "dmg-black", "dmg-mixed");
  gameDetailsDmgType.title = "";
  gameDetailsDmgType.innerHTML = `<span>-</span>`;
  gameDetailsDmgAmount.textContent = "-";
  gameDetailsGoodRange.textContent = "-";
  gameDetailsBadRange.textContent = "-";
  gameDetailsBaseName.classList.add("hidden");
  gameDetailsBaseCode.classList.add("hidden");
  gameDetailsBaseRisk.classList.add("hidden");
  gameDetailsDmgType.classList.add("hidden");
  gameDetailsDmgAmount.classList.add("hidden");
  gameDetailsGoodRange.classList.add("hidden");
  gameDetailsBadRange.classList.add("hidden");
  const button = document.getElementById("detailsBaseUnlockButton");
  if (button) {
    button.addEventListener("click", () => {
      playSound("unlockUi");
      unlockDetailsPart("/api/details/base").catch((error) =>
        handleDetailsActionError("базовую информацию", error).catch((modalError) => showRuntimeErrorModal(modalError, { actionLabel: "базовую информацию" }))
      );
    });
  }
}

function renderDetailsHiddenHint(details) {
  const hidden = details.hidden_hint || {};
  gameDetailsHiddenHintSlot.innerHTML = "";
  gameDetailsHintsList.classList.toggle("no-hidden", !hidden.exists);
}

function renderDetailsHints(details) {
  const hints = details.hints || [];
  const hidden = details.hidden_hint || {};
  const companionOffer = normalizeCompanionOffer(details.companion_offer || null);
  const cards = [];

  if (hidden.exists) {
    if (hidden.unlocked && hidden.can_open && hidden.text) {
      cards.push(`
        <article class="game-details-hint-card unlocked hidden-variant">
          <div class="game-details-hint-label">Скрытая подсказка</div>
          <div class="game-details-hint-text">${formatHintMarkup(hidden.text)}</div>
        </article>
      `);
    } else {
      cards.push(`
        <article class="game-details-hint-card hidden-variant">
          <button class="game-details-hint-button hidden-hint ${hidden.can_open ? "" : "locked"}" id="detailsHiddenHintButton" type="button" ${hidden.can_open ? "" : "disabled"} title="${hidden.can_open ? "Открыть скрытую подсказку" : "Для открытия требуется артефакт"}">
            <span class="game-details-hint-left">
              <img src="/photo/work_room/hinthidden.png" alt="Скрытая подсказка">
            </span>
            <span class="game-details-hint-right">Скрытая подсказка</span>
          </button>
        </article>
      `);
    }
  }

  if (!hints.length && !cards.length) {
    gameDetailsHintsList.innerHTML = `<div class="game-details-empty-note">Подсказок нет</div>`;
    return;
  }

  cards.push(...hints.map((hint) => {
    if (hint.unlocked) {
      const pendingCompanion = Boolean(companionOffer && companionOffer.hintIndex === Number(hint.index));
      const pendingContract = Boolean(hint.pending_contract);
      const pendingStatConversion = Boolean(hint.pending_stat_conversion);
      const pendingChooseBonus = Boolean(hint.pending_choose_bonus);
      const pendingDeathShield = Boolean(hint.pending_death_shield);
      const pendingAltarOffering = Boolean(hint.pending_altar_offering);
      const pendingDevilDeal = Boolean(hint.pending_devil_deal);
      const pendingFreeStat = Boolean(hint.pending_free_stat);
      const pendingCurse137 = Boolean(hint.pending_curse137);
      return `
        <article class="game-details-hint-card unlocked ${pendingCompanion ? "pending-companion" : ""} ${pendingContract || pendingStatConversion || pendingChooseBonus || pendingDeathShield || pendingAltarOffering || pendingDevilDeal || pendingFreeStat || pendingCurse137 ? "pending-contract" : ""}" ${pendingCompanion ? `data-pending-companion="${hint.index}"` : ""} ${pendingContract ? `data-pending-contract="${hint.index}" tabindex="0" role="button"` : ""} ${pendingStatConversion ? `data-pending-stat-conversion="${hint.index}" tabindex="0" role="button"` : ""} ${pendingChooseBonus ? `data-pending-choose-bonus="${hint.index}" tabindex="0" role="button"` : ""} ${pendingDeathShield ? `data-pending-death-shield="${hint.index}" tabindex="0" role="button"` : ""} ${pendingAltarOffering ? `data-pending-altar-offering="${hint.index}" tabindex="0" role="button"` : ""} ${pendingDevilDeal ? `data-pending-devil-deal="${hint.index}" tabindex="0" role="button"` : ""} ${pendingFreeStat ? `data-pending-free-stat="${hint.index}" tabindex="0" role="button"` : ""} ${pendingCurse137 ? `data-pending-curse137="${hint.index}" tabindex="0" role="button"` : ""}>
          <div class="game-details-hint-label">Руководство по обращению ${hint.index}</div>
          <div class="game-details-hint-text">${formatHintMarkup(hint.text)}</div>
        </article>
      `;
    }
    const nextIndex = Number(currentDetailsPayload?.progress?.hintunlocked || 0) + 1;
    const clickable = hint.index === nextIndex;
    return `
      <article class="game-details-hint-card">
        <button class="game-details-hint-button ${clickable ? "" : "locked"}" data-hint-index="${hint.index}" type="button" ${clickable ? "" : "disabled"}>
          <span class="game-details-hint-left">
            <img src="/photo/work_room/hintunlock.png" alt="Открыть подсказку">
            <span class="game-details-unlock-cost">${hint.cost ?? detailsHintCost(hint.index)}</span>
          </span>
          <span class="game-details-hint-right">Руководство по обращению ${hint.index}</span>
        </button>
        </article>
    `;
  }));

  gameDetailsHintsList.innerHTML = cards.join("");
  const hiddenButton = document.getElementById("detailsHiddenHintButton");
  if (hiddenButton && hidden.can_open) {
    hiddenButton.addEventListener("click", () => {
      playSound("unlockUi");
      apiPost("/api/details/hidden-hint", {
        user_id: currentUserId(),
        anomaly_id: activeRoomAnomalyId
      }).then((payload) => {
        renderDetailsScreen(payload.details);
      }).catch((error) =>
        handleDetailsActionError("скрытую подсказку", error).catch((modalError) => showRuntimeErrorModal(modalError, { actionLabel: "скрытую подсказку" }))
      );
    });
  }
  gameDetailsHintsList.querySelectorAll("[data-hint-index]").forEach((button) => {
    button.addEventListener("click", () => {
      playSound("unlockUi");
      unlockDetailsPart("/api/details/hint").catch((error) =>
        handleDetailsActionError("подсказку", error).catch((modalError) => showRuntimeErrorModal(modalError, { actionLabel: "подсказку" }))
      );
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-companion]").forEach((node) => {
    node.addEventListener("click", () => {
      openCompanionOfferModal(companionOffer).catch((error) => showRuntimeErrorModal(error));
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-contract]").forEach((node) => {
    const reopenContract = () => openKillContractOffer(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenContract);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenContract();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-stat-conversion]").forEach((node) => {
    const reopenConversion = () => openStatConversionOffer(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenConversion);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenConversion();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-choose-bonus]").forEach((node) => {
    const reopenChooseBonus = () => openChooseBonusOffer(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenChooseBonus);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenChooseBonus();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-death-shield]").forEach((node) => {
    const reopenDeathShield = () => openDeathShieldOffer(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenDeathShield);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenDeathShield();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-altar-offering]").forEach((node) => {
    const reopenOffering = () => openAltarOffering(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenOffering);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenOffering();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-devil-deal]").forEach((node) => {
    const reopenDeal = () => openDevilDeal(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenDeal);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenDeal();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-free-stat]").forEach((node) => {
    const reopenGift = () => openFreeStatOffer(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenGift);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenGift();
      }
    });
  });
  gameDetailsHintsList.querySelectorAll("[data-pending-curse137]").forEach((node) => {
    const reopenCurse = () => openCurse137Offer(activeRoomAnomalyId).catch((error) => showRuntimeErrorModal(error));
    node.addEventListener("click", reopenCurse);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        reopenCurse();
      }
    });
  });
}

function renderDetailsDescription(details) {
  if (details.description_unlocked) {
    gameDetailsDescriptionSlot.innerHTML = `<div class="game-details-description-text">${details.description || "Описание пока отсутствует."}</div>`;
    return;
  }
  gameDetailsDescriptionSlot.innerHTML = `
    <button class="game-details-description-button" id="detailsDescriptionButton" type="button">
      <span class="game-details-description-image-wrap">
        <img src="/photo/work_room/description.png" alt="Описание">
        <span class="game-details-description-cost">${details.description_unlock_cost || 10}</span>
      </span>
      <span class="game-details-description-button-label">ПОЛНАЯ ИСТОРИЯ</span>
    </button>
  `;
  const button = document.getElementById("detailsDescriptionButton");
  if (button) {
    button.addEventListener("click", () => {
      playSound("unlockUi");
      unlockDetailsPart("/api/details/description").catch((error) =>
        handleDetailsActionError("полное описание", error).catch((modalError) => showRuntimeErrorModal(modalError, { actionLabel: "полное описание" }))
      );
    });
  }
}

function renderDetailsPreferences(details) {
  const container = document.getElementById("gameDetailsPreferences");
  if (!container) return;
  const preferences = Array.isArray(details.preferences) ? details.preferences : [];
  if (details.chance_locked || !preferences.length) {
    container.classList.remove("unlocked");
    container.innerHTML = `<img src="/photo/work_room/chancelocked.png" alt="Предпочтения заблокированы">`;
    return;
  }
  container.classList.add("unlocked");
  container.innerHTML = preferences.map((item) => `
    <div class="game-details-preference-item" title="${escapeHtml(item.label || "Работа")}: ${Number(item.chance || 0)}%">
      <img src="${escapeHtml(item.icon || "")}" alt="${escapeHtml(item.label || "Работа")}">
      <div class="game-details-preference-copy">
        <span>${escapeHtml(item.label || "Работа")}</span>
        <strong>${Number(item.chance || 0)}%</strong>
      </div>
    </div>
  `).join("");
}

function renderDetailsScreen(details) {
  const maxScroll = Math.max(0, gameDetailsHintsList.scrollHeight - gameDetailsHintsList.clientHeight);
  const scrollRatio = maxScroll > 0 ? gameDetailsHintsList.scrollTop / maxScroll : 0;
  publishCameraState("details", activeRoomAnomalyId || details?.anomaly_id, true, {
    details_scroll_ratio: scrollRatio
  });
  currentDetailsPayload = details;
  gameDetailsProgressValue.textContent = `${details.progress_percent ?? 0}%`;
  if ((details.progress_percent ?? 0) >= 100) {
    gameDetailsProgressNote.textContent = "исследование завершено. Для получения награды нажмите кнопку завершить работу";
    gameDetailsProgressNote.classList.remove("hidden");
    if (!completionAlertPlayed) {
      playSound("researchComplete");
      completionAlertPlayed = true;
    }
  } else {
    gameDetailsProgressNote.textContent = "";
    gameDetailsProgressNote.classList.add("hidden");
    completionAlertPlayed = false;
  }
  gameDetailsRpValue.textContent = details.rp_hidden ? "?" : String(details.rp ?? 0);
  gameDetailsKlipotaValue.textContent = String(details.klipota ?? 0);
  gameDetailsEscapeText.textContent = details.escape_text || "НЕ СБЕГАЕТ";
  renderDetailsBase(details);
  renderDetailsHiddenHint(details);
  renderDetailsHints(details);
  renderDetailsDescription(details);
  renderDetailsPreferences(details);
}

async function openDetailsScreen() {
  if (!activeRoomAnomalyId) return;
  closeInventoryModal();
  const payload = await api(`/api/details?user_id=${currentUserId()}&anomaly_id=${activeRoomAnomalyId}`);
  renderDetailsScreen(payload.details);
  gameRoomScreen.classList.add("hidden");
  gameDetailsScreen.classList.remove("hidden");
  if (payload.details?.companion_offer?.pending) {
    await openCompanionOfferModal(payload.details.companion_offer);
    return;
  }
}

async function unlockDetailsPart(path) {
  if (!activeRoomAnomalyId) return;
  const payload = await apiPost(path, {
    user_id: currentUserId(),
    anomaly_id: activeRoomAnomalyId
  });
  if (payload.room) {
    renderWorkRoom(payload.room);
  }
  renderDetailsScreen(payload.details);
  gameRoomScreen.classList.add("hidden");
  gameDetailsScreen.classList.remove("hidden");
  if (path === "/api/details/base") {
    applyDamageFeedback(payload);
  }
  if (payload.effect_result?.damage && payload.effect_result?.event?.type !== "stat_checks") {
    applyDamageFeedback(payload.effect_result);
  }
  if (payload.damage?.shield_triggered || payload.effect_result?.damage?.shield_triggered) {
    await showDeathShieldMiracleModal(payload.damage || payload.effect_result.damage);
  }
  if (payload.effect_result?.event) {
    const handled = await handleQueuedUiEvent(payload.effect_result, payload.details);
    if (handled) return;
  }
  if (payload.effect_result?.companion_offer || payload.details?.companion_offer?.pending) {
    await openCompanionOfferModal(payload.effect_result?.companion_offer || payload.details?.companion_offer);
    return;
  }
  if (payload.effect_result?.modal) {
    await showDetailsInfoModal({
      intro: payload.effect_result.modal.intro || payload.effect_result.title || "",
      effect: payload.effect_result.modal.effect || payload.effect_result.description || "",
      icon: payload.effect_result.modal.icon || payload.effect_result.modal.iconSrc || "/photo/work_room/success.png",
      iconAlt: payload.effect_result.modal.iconAlt || "Эффект"
    });
    if (payload.effect_result?.deferred_fatal_action) {
      deferFinalResultsModal = true;
      try {
        const fatalPayload = await apiPost("/api/details/confirm-fatal", {
          user_id: currentUserId(),
          anomaly_id: activeRoomAnomalyId,
          action_type: payload.effect_result.deferred_fatal_action.type
        });
        if (fatalPayload.player_dead) {
          deferFinalResultsModal = false;
          if (showFinalResults(fatalPayload.final_results || fatalPayload.game_state?.final_results)) {
            return;
          }
          if (fatalPayload.game_state?.game?.started) {
            await applyGameState(fatalPayload.game_state, { forceRefresh: true });
            return;
          }
          try {
            const refreshedGame = await api(`/api/game?user_id=${currentUserId()}`);
            if (showFinalResults(refreshedGame?.final_results)) {
              return;
            }
            if (refreshedGame?.game?.started) {
              await applyGameState(refreshedGame, { forceRefresh: true });
              return;
            }
          } catch (_) {}
          closeGameScreen();
          return;
        }
        if (fatalPayload.game_state?.game?.started) {
          deferFinalResultsModal = false;
          await applyGameState(fatalPayload.game_state, { forceRefresh: true });
          return;
        }
      } finally {
        deferFinalResultsModal = false;
      }
    }
    if (payload.effect_result?.fatal_after_modal) {
      deferFinalResultsModal = true;
      try {
        await showDeathModal(payload.effect_result.fatal_after_modal.reason || "Сотрудник погиб.");
      } finally {
        deferFinalResultsModal = false;
      }
      if (showFinalResults(payload.effect_result.fatal_after_modal.game_state?.final_results || payload.game_state?.final_results)) {
        return;
      }
      if (payload.effect_result.fatal_after_modal.game_state?.game?.started || payload.game_state?.game?.started) {
        await applyGameState(payload.effect_result.fatal_after_modal.game_state || payload.game_state, { forceRefresh: true });
        return;
      }
      closeGameScreen();
    }
    return;
  }
  if (payload.effect_result?.description) {
    showInfoToast(payload.effect_result.description);
  }
}

async function finishResearchDetails() {
  if (!activeRoomAnomalyId) return;
  const payload = await apiPost("/api/details/finish", {
    user_id: currentUserId(),
    anomaly_id: activeRoomAnomalyId
  });
  renderDetailsScreen(payload.details);
}

function closeStatUpgradeModal() {
  statUpgradeOverlay.classList.add("hidden");
}

function renderStatUpgradeModal(upgrade) {
  statUpgradeReward.textContent = `Получено ${Number(lastFinishReward?.cp ?? 0)} Соревновательных очков и ${Number(lastFinishReward?.rt ?? 0)} очков прокачки.`;
  const points = Number(upgrade?.points_available ?? 0);
  statUpgradePoints.textContent = `В наличии ${points} очков прокачки`;
  statUpgradeList.innerHTML = (upgrade?.stats || []).map((item) => {
    const costLabel = item.maxed ? "MAX" : `(${item.cost})`;
    const blockedReason = item.blocked_reason ? ` title="${escapeHtml(item.blocked_reason)}"` : "";
    return `
      <div class="stat-upgrade-item">
        <img class="stat-upgrade-icon" src="${item.icon}" alt="${item.label}">
        <div class="stat-upgrade-copy">
          <div class="stat-upgrade-name">${item.label}</div>
          <div class="stat-upgrade-meta">${item.effect || ""}</div>
        </div>
        <div class="stat-upgrade-level">L ${item.level}</div>
        <div class="stat-upgrade-cost">${costLabel}</div>
        <button class="stat-upgrade-plus ${item.can_upgrade ? "" : "disabled"}" data-stat-upgrade="${item.key}" type="button" ${item.can_upgrade ? "" : "disabled"}${blockedReason}>+</button>
      </div>
    `;
  }).join("");
  statUpgradeOverlay.classList.remove("hidden");
}

async function openStatUpgradeModal() {
  const payload = await apiPost("/api/game/finish-preview", {
    user_id: currentUserId(),
  });
  finishPreviewActive = true;
  lastFinishReward = payload.reward?.already_claimed
    ? { cp: 0, rt: 0 }
    : { cp: Number(payload.reward?.cp || 0), rt: Number(payload.reward?.rt || 0) };
  if (payload.room) {
    renderWorkRoom(payload.room);
  }
  if (payload.clay_penalty?.triggered) {
    applyDamageFeedback({ damage: payload.clay_penalty.damage });
    await showInfoModal("Глиняная статуя", payload.clay_penalty.message || "Статуя рассыпалась.", {
      iconSrc: "/photo/work_room/badresult.png",
      iconAlt: "Глиняная статуя"
    });
    if (payload.clay_penalty.player_dead) {
      await showDeathModal(payload.clay_penalty.damage?.death_reason || "Глиняная статуя истощила разум владельца.");
      if (payload.game_state?.game?.started) {
        await applyGameState(payload.game_state, { forceRefresh: true });
      } else {
        showFinalResults(payload.game_state?.final_results);
      }
      return;
    }
  }
  if (payload.anomaly62_fate?.triggered) {
    applyDamageFeedback({ damage: payload.anomaly62_fate.damage });
    await showInfoModal("Бог пепельной чумы", payload.anomaly62_fate.message || "Вы приняли свою судьбу.", {
      iconSrc: "/photo/work_room/badresult.png",
      iconAlt: "Бог пепельной чумы"
    });
    if (payload.anomaly62_fate.player_dead) {
      await showDeathModal(payload.anomaly62_fate.damage?.death_reason || "Принял свою судьбу по воле Бога пепельной чумы");
      if (payload.game_state?.game?.started) await applyGameState(payload.game_state, { forceRefresh: true });
      else showFinalResults(payload.game_state?.final_results);
      return;
    }
  }
  if (payload.alastor_resolution?.pending) {
    const alastorResult = await showAlastorResolutionIfPending(payload.alastor_resolution);
    if (alastorResult?.player_dead) return;
  }
  if (payload.ilvetal_notice?.pending || payload.room?.ilvetal_notice?.pending) {
    await showIlvetalNoticeIfPending(payload.ilvetal_notice || payload.room?.ilvetal_notice, {
      anomalyId: payload.room?.anomaly_id || activeRoomAnomalyId
    });
  }
  renderStatUpgradeModal(payload.upgrade || { points_available: 0, stats: [] });
}

async function upgradeStat(statKey) {
  const payload = await apiPost("/api/game/upgrade-stat", {
    user_id: currentUserId(),
    stat_key: statKey,
  });
  if (payload.room) {
    renderWorkRoom(payload.room);
  }
  renderStatUpgradeModal(payload.upgrade || { points_available: 0, stats: [] });
}

async function confirmFinishTurn() {
  const payload = await apiPost("/api/game/finish-turn", {
    user_id: currentUserId(),
  });
  finishPreviewActive = false;
  lastFinishReward = { cp: 0, rt: 0 };
  closeStatUpgradeModal();
  activeGameSignature = null;
  activeRoomPayload = null;
  currentDetailsPayload = null;
  if (payload.game_state?.game?.started) {
    await applyGameState(payload.game_state, { forceRefresh: true });
    return;
  }
  if (showFinalResults(payload.game_state?.final_results)) {
    return;
  }
  closeGameScreen();
  onlineScreen.classList.remove("hidden");
  openOnlineRoomView();
  await loadOnlineLobby();
}

async function finishWorkAction() {
  if (activeRoomPayload?.can_finish_turn || activeRoomPayload?.reward_claimed) {
    await openStatUpgradeModal();
    return;
  }
  showToast("Завершить работу");
}

async function fleeWorkAction() {
  if (!activeRoomPayload || roomWorkResolving) return;
  roomWorkResolving = true;
  setWorkButtonsDisabled(true);
  try {
    const playerName = discordUser?.global_name || discordUser?.username || "Сотрудник";
    const anomalyName = activeRoomPayload.display_name || activeRoomPayload.name || "НЕИЗВЕСТНЫЙ ОБЪЕКТ";
    const activeEffects = Array.isArray(activeRoomPayload?.player_stats?.effects)
      ? activeRoomPayload.player_stats.effects
      : [];
    const fleeIsDeath = activeEffects.some((effect) => {
      const key = String(effect?.key || effect?.raw || "").trim();
      return key === "FleeIsDeath";
    });
    let previewText = `Сотрудник "${playerName}" решил прекратить изучение и сбежал из камеры заключения аномалии ${anomalyName}...`;
    if (fleeIsDeath) {
      previewText += " Но аномалия прикончила сотрудника.";
    }
    await showInfoModal(previewText, "", {
      iconSrc: activeRoomPayload?.model_url || "/photo/work_room/404.png",
      iconAlt: "Аномалия"
    });
    const payload = await apiPost("/api/game/flee", {
      user_id: currentUserId()
    });
    if (payload.alastor_resolution?.pending) {
      const alastorResult = await showAlastorResolutionIfPending(payload.alastor_resolution);
      if (alastorResult?.player_dead) return;
    }
    finishPreviewActive = false;
    lastFinishReward = { cp: 0, rt: 0 };
    closeStatUpgradeModal();
    activeRoomPayload = null;
    currentDetailsPayload = null;
    if (payload.player_dead) {
      await showDeathModal(getDeathReasonFromPayload(payload));
      if (showFinalResults(payload.game_state?.final_results)) {
        return;
      }
    }
    if (payload.game_state?.game?.started) {
      await applyGameState(payload.game_state, { forceRefresh: true });
      return;
    }
    if (showFinalResults(payload.game_state?.final_results)) {
      return;
    }
    closeGameScreen();
    onlineScreen.classList.remove("hidden");
    openOnlineRoomView();
    await loadOnlineLobby();
  } finally {
    roomWorkResolving = false;
    setWorkButtonsDisabled(false);
  }
}

function openSurrenderConfirmation() {
  if (!gameSurrenderButton || gameSurrenderButton.disabled) return;
  const restoreHiddenRoom = spectatorMode && gameRoomScreen.classList.contains("hidden");
  if (restoreHiddenRoom) gameRoomScreen.classList.remove("hidden");
  const restoreSpectatorScreen = () => {
    if (restoreHiddenRoom) gameRoomScreen.classList.add("hidden");
  };
  showEventChoiceModal({
    icon: "/photo/work_room/heartattack.png",
    iconAlt: "Смерть",
    intro: "Вы уверены?",
    effect: "Это приведет к смерти и закончит для вас игру.",
    choices: [
      {
        label: "Сдаться",
        className: "danger",
        onSelect: async () => {
          gameSurrenderButton.disabled = true;
          closeEventModal();
          restoreSpectatorScreen();
          try {
            const payload = await apiPost("/api/game/surrender", { user_id: currentUserId() });
            await showDeathModal(payload.death_reason || "Сдался");
            if (showFinalResults(payload.game_state?.final_results)) return;
            if (payload.game_state?.game?.started) {
              activeGameSignature = null;
              activeRoomPayload = null;
              currentDetailsPayload = null;
              await applyGameState(payload.game_state, { forceRefresh: true });
            }
          } catch (error) {
            restoreSpectatorScreen();
            showRuntimeErrorModal(error);
          }
        }
      },
      { label: "Отмена", onSelect: async () => { closeEventModal(); restoreSpectatorScreen(); } }
    ]
  });
}

async function closeDetailsScreen(refreshRoom = true) {
  gameDetailsLightbox.classList.add("hidden");
  gameDetailsScreen.classList.add("hidden");
  gameRoomScreen.classList.remove("hidden");
  if (!spectatorMode && activeRoomAnomalyId) {
    publishCameraState("room", activeRoomAnomalyId, true);
  }
  if (refreshRoom && activeRoomAnomalyId) {
    try {
      const payload = await api(`/api/work-room?user_id=${currentUserId()}&anomaly_id=${activeRoomAnomalyId}`);
      renderWorkRoom(payload.room);
    } catch (_) {}
  }
}

function hideRoomMenus() {
  gameRoomActionMenu.classList.add("hidden");
  gameRoomWorkMenu.classList.add("hidden");
  gameRoomRiskMenu.classList.add("hidden");
  gameRoomTypeMenu.classList.add("hidden");
  gameRoomResultMenu.classList.add("hidden");
}

function openActionMenu() {
  hideRoomMenus();
  gameRoomActionMenu.classList.remove("hidden");
  gameRoomWorkMeta.textContent = "";
  if (pendingNextWorkDebug) {
    renderWorkDebug(pendingNextWorkDebug);
  }
}

function openWorkMenu() {
  hideRoomMenus();
  gameRoomWorkMenu.classList.remove("hidden");
  gameRoomWorkMeta.textContent = "";
  if (pendingNextWorkDebug) {
    renderWorkDebug(pendingNextWorkDebug);
  }
}

function openRiskMenu() {
  hideRoomMenus();
  gameRoomRiskMenu.classList.remove("hidden");
  gameRoomWorkMeta.textContent = "";
}

function openTypeMenu() {
  hideRoomMenus();
  gameRoomTypeMenu.classList.remove("hidden");
  gameRoomWorkMeta.textContent = "";
}

function openResultMenu() {
  hideRoomMenus();
  gameRoomResultMenu.classList.remove("hidden");
  gameRoomWorkMeta.textContent = "";
}

function setResultMenuDisabled(disabled) {
  [actionRepeatWorkButton, actionChangeWorkButton, actionReturnMenuButton].forEach((button) => {
    button.disabled = disabled;
    button.classList.toggle("disabled", disabled);
  });
}

function setFinishButtonState(enabled) {
  actionFinishButton.disabled = !enabled;
  actionFinishButton.classList.toggle("disabled", !enabled);
  actionFinishButton.classList.toggle("is-active", !!enabled);
}

function renderWorkRoom(room) {
  publishCameraState("room", room?.anomaly_id);
  const previousAnomalyId = activeRoomAnomalyId;
  activeRoomPayload = room;
  activeRoomAnomalyId = room.anomaly_id;
  applyAnomalyCustomButtons(room);
  if (previousAnomalyId !== null && Number(previousAnomalyId) !== Number(room.anomaly_id)) {
    resetRoomResultGrid();
    finishPreviewActive = false;
    lastFinishReward = { cp: 0, rt: 0 };
    closeStatUpgradeModal();
    pendingNextWorkDebug = null;
    alastorTaskSignature = "";
  }
  gameWaitingScreen.classList.add("hidden");
  gameSelectScreen.classList.add("hidden");
  gameRoomScreen.classList.remove("hidden");
  try {
    const brainrot = room?.brainrot_music || {};
    if (brainrot.active && Array.isArray(brainrot.tracks) && brainrot.tracks.length) {
      if (Number(brainrot.day || 0) !== brainrotMusicDay || !brainrotMusicUrl) {
        brainrotMusicDay = Number(brainrot.day || 0);
        brainrotMusicUrl = brainrot.tracks[Math.floor(Math.random() * brainrot.tracks.length)];
      }
    }
    if (!x125AudioLock && !sovuhVnActive) ensureGameMusic(brainrot.active ? "brainrot" : "ambient").play().catch(() => {});
  } catch (_) {}

  gameRoomName.textContent = room.display_name || "НЕИЗВЕСТНЫЙ ОБЪЕКТ";
  gameRoomRpValue.textContent = room.rp_hidden ? "?" : String(room.rp ?? 0);
  gameRoomModel.src = room.model_url || "/photo/work_room/404.png";
  gameRoomModel.alt = room.display_name || "Аномалия";
  gameRoomModel.classList.remove(
    "model-size-tiny", "model-size-small", "model-size-normal", "model-size-large",
    "model-placeholder", "model-dimmed", "model-bottom-aligned"
  );
  const modelSize = ["tiny", "small", "normal", "large"].includes(room.model_size) ? room.model_size : "placeholder";
  gameRoomModel.classList.add(modelSize === "placeholder" ? "model-placeholder" : `model-size-${modelSize}`);
  gameRoomModel.classList.toggle("model-dimmed", !!room.model_dimmed);
  gameRoomModel.classList.toggle("model-bottom-aligned", [23, 38, 56, 78, 133].includes(Number(room.anomaly_id)));
  if (gameRoomAgent) {
    const agentUrl = String(room.agent_model_url || "");
    gameRoomAgent.classList.toggle("hidden", !agentUrl);
    if (agentUrl) {
      gameRoomAgent.src = agentUrl;
      gameRoomAgent.alt = `Персонаж игрока char${Number(room.agent_character || 0)}`;
    } else {
      gameRoomAgent.removeAttribute("src");
    }
  }

  gameRoomNoRisk.classList.remove("hidden");
  gameRoomNoRisk.classList.toggle("is-known", !!(room.show_risk && room.risk_icon));
  gameRoomNoRisk.classList.toggle("is-unknown", !(room.show_risk && room.risk_icon));
  gameRoomNoRisk.src = room.show_risk && room.risk_icon ? room.risk_icon : "/photo/work_room/norisks.png";
  gameRoomNoRisk.alt = room.show_risk ? (room.risk_label || "Класс опасности") : "Неизвестный класс";
  gameRoomKlipotaBadge.classList.remove("hidden");
  gameRoomKlipotaMark.textContent = room.show_klipota ? String(room.klipota ?? 0) : "?";

  gameRoomPenalty.classList.toggle("hidden", !room.show_penalty);
  gameRoomPenalty.classList.remove("penalty-low", "penalty-mid", "penalty-high");
  if (room.show_penalty) {
    gameRoomPenalty.textContent = `-${room.penalty}%`;
    const penaltyValue = Number(room.penalty ?? 0);
    if (penaltyValue >= 21) {
      gameRoomPenalty.classList.add("penalty-high");
    } else if (penaltyValue >= 11) {
      gameRoomPenalty.classList.add("penalty-mid");
    } else if (penaltyValue > 0) {
      gameRoomPenalty.classList.add("penalty-low");
    }
  }

  renderWorkHints(room.works || []);
  renderWorkDebug(room.debug || null);
  renderGlobalDebug(room.debug_globals || []);
  renderAdminStats(room.player_stats || null);
  renderPlayerStatus(room.player_status || null);
  setFinishButtonState(!!room.can_finish_turn);
  setResearchLockedState(!!room.research_locked, room.research_locked_reason || "");
  applyAnomalyActionLock(room);
  const protocol = room.protocol_x || {};
  const hasProtocol = !!protocol.owned;
  actionArtifactButton.classList.toggle("hidden", !hasProtocol);
  if (hasProtocol) {
    actionArtifactButton.textContent = protocol.used_today ? "Протокол X использован" : "Протокол X";
    actionArtifactButton.disabled = !protocol.available;
    actionArtifactButton.classList.toggle("disabled", !protocol.available);
    actionArtifactButton.title = protocol.used_today
      ? "Способность уже использована сегодня."
      : (!protocol.is_turn ? "Сейчас не ваш ход." : (!(protocol.targets || []).length ? "Нет доступных целей." : ""));
  }

  const workButtons = workButtonMap();
  (room.works || []).forEach((item) => {
    const button = workButtons[item.key];
    if (!button) return;
    button.dataset.workType = item.key;
    button.dataset.blocked = item.blocked ? "true" : "false";
    button.title = "";
    button.disabled = !!item.blocked;
    button.classList.toggle("disabled", !!item.blocked);
  });
  const voyagerDanger=room.voyager_danger;
  if(voyagerDanger?.work&&voyagerDanger.event_id){
    const flashKey=`voyager-solo-flash:${currentUserId()}:${voyagerDanger.event_id}`;
    if(window.localStorage.getItem(flashKey)!=="shown"){
      window.localStorage.setItem(flashKey,"shown");
      const dangerButton=workButtons[voyagerDanger.work],dangerLabel=dangerButton?.querySelector(".game-room-work-label");
      if(dangerLabel){
        dangerLabel.classList.add("voyager-danger-flash");
        window.setTimeout(()=>dangerLabel.classList.remove("voyager-danger-flash"),Number(voyagerDanger.flash_ms||1000));
      }
    }
  }
  if (roomWorkResolving) {
    setWorkButtonsDisabled(true);
  }
  if (!roomWorkResolving && !finishPreviewActive) {
    openActionMenu();
  }
}

async function openWorkRoom(anomalyId, options = {}) {
  finishPreviewActive = false;
  lastFinishReward = { cp: 0, rt: 0 };
  closeStatUpgradeModal();
  gameDayText.textContent = "";
  gameDayOverlay.classList.remove("hidden");
  gameDayOverlay.classList.add("transition");
  gameSelectScreen.classList.add("hidden");
  gameWaitingScreen.classList.add("hidden");
  if (!options.skipTransition) {
    await new Promise((resolve) => window.setTimeout(resolve, 320));
  }
  const payload = await api(`/api/work-room?user_id=${currentUserId()}&anomaly_id=${anomalyId}&apply_initial=1`);
  renderWorkRoom(payload.room);
  const initialEffectAnimation = payload.initial_effect_result ? playInitialEffectAnimation() : Promise.resolve();
  if (payload.initial_effect_result?.description) {
    showInfoToast(payload.initial_effect_result.description);
  }
  await initialEffectAnimation;
  await new Promise((resolve) => window.setTimeout(resolve, 160));
  gameDayOverlay.classList.add("hidden");
  gameDayOverlay.classList.remove("transition");
  await handleKlipotaEvent(payload.room?.klipota_event);
  if (payload.initial_effect_result?.event) {
    const handled = await handleQueuedUiEvent(payload.initial_effect_result, null);
    if (handled) return;
  }
  if (payload.room?.contract_summary?.pending) {
    const handled = await showContractSummaryIfPending(payload.room);
    if (handled) {
      return;
    }
  }
  if (payload.room?.contract_warning?.pending) {
    await showContractWarningIfPending(payload.room);
  }
  if (payload.room?.ilvetal_notice?.pending) {
    await showIlvetalNoticeIfPending(payload.room.ilvetal_notice, {
      anomalyId: payload.room?.anomaly_id || anomalyId
    });
  }
  if (payload.room?.cheaptrick_notice?.pending) {
    await showCheapTrickNoticeIfPending(payload.room.cheaptrick_notice, {
      anomalyId: payload.room?.anomaly_id || anomalyId
    });
  }
  if (payload.room?.companion_notice?.pending) {
    await showInfoModal(payload.room.companion_notice.description || "", payload.room.companion_notice.title || "", {
      iconSrc: payload.room.companion_notice.icon || "/photo/work_room/neutralresult.png",
      iconAlt: payload.room.companion_notice.iconAlt || "Компаньон"
    });
  }
}

async function runWork(workType) {
  if (!activeRoomAnomalyId) return;
  hideRoomMenus();
  roomWorkResolving = true;
  setWorkButtonsDisabled(true);
  gameRoomWorkMeta.textContent = "Выполняется работа...";
  gameRoomResultScore.textContent = "";
  gameRoomResultScore.classList.add("hidden-score");
  gameRoomRpValue.textContent = "...";
  try {
    const payload = await apiPost("/api/work", {
      user_id: currentUserId(),
      anomaly_id: activeRoomAnomalyId,
      work_type: workType,
      chosen_class: selectedRiskChoice,
      chosen_type: selectedTypeChoice
    });
    if(payload.room)renderWorkRoom(payload.room);
    pendingNextWorkDebug = payload.debug_after || null;
    renderWorkDebug(payload.debug || null);
    gameRoomRpValue.textContent = "...";
    if (payload.damage?.shield_triggered) {
      await showDeathShieldMiracleModal(payload.damage);
    }
    if (payload.damage?.clay_overloaded) {
      await showInfoModal(
        "Глиняная статуя переполнена",
        "Статуя накопила 200 урона рассудку и взорвалась. Получено 100 урона рассудку, предмет уничтожен.",
        { iconSrc: "/photo/work_room/badresult.png", iconAlt: "Разрушенная статуя" }
      );
    }
    if (payload.damage?.laplace_message) {
      await showInfoModal("Цепи демона разорваны", payload.damage.laplace_message, {
        iconSrc: "/photo/work_room/success.png",
        iconAlt: "Освобождение от проклятия Лапласа"
      });
    }
    await handleMentalEvents(payload);
    if (payload.player_dead) {
      await showDeathModal(getDeathReasonFromPayload(payload));
      if (showFinalResults(payload.game_state?.final_results)) {
        return;
      }
      closeGameScreen();
      closeOnlineScreen();
      closePlayScreen();
      return;
    }
    openResultMenu();
    setResultMenuDisabled(true);
    if (payload.result_hidden) {
      renderHiddenRoomResult();
    } else {
      renderRoomResult(payload.rolls || [], payload.room?.rp);
    }
    gameRoomWorkMeta.textContent = "";
    const resultDelay = (payload.rolls || []).length * 140 + 180;
    if (payload.cheaptrick_fatal_action?.pending) {
      await new Promise((resolve) => window.setTimeout(resolve, resultDelay));
      const fatalPayload = await apiPost("/api/game/resolve-cheaptrick-fatal", {
        user_id: currentUserId(),
        anomaly_id: payload.cheaptrick_fatal_action.anomaly_id || activeRoomAnomalyId
      });
      roomWorkResolving = false;
      await showDeathModal(fatalPayload.death_reason || payload.cheaptrick_fatal_action.reason || "Сотрудник погиб.");
      if (showFinalResults(fatalPayload.final_results || fatalPayload.game_state?.final_results)) {
        return;
      }
      if (fatalPayload.game_state?.game?.started) {
        await applyGameState(fatalPayload.game_state, { forceRefresh: true });
        return;
      }
      closeGameScreen();
      closeOnlineScreen();
      closePlayScreen();
      return;
    }
    window.setTimeout(() => {
      setResultMenuDisabled(false);
      roomWorkResolving = false;
    }, resultDelay);
  } catch (error) {
    roomWorkResolving = false;
    setResultMenuDisabled(false);
    openActionMenu();
    await showRuntimeErrorModal(error);
  } finally {
    setWorkButtonsDisabled(false);
  }
}

function startWorkFlow(workType) {
  if (Number(activeRoomPayload?.anomaly_id) === 11 && workType === "suppression") {
    openResetAction().catch((error) => showRuntimeErrorModal(error));
    return;
  }
  if (Number(activeRoomPayload?.anomaly_id) === 63) {
    openAlastorDeal(Number(activeRoomPayload?.anomaly_id)).catch((error) => showRuntimeErrorModal(error));
    return;
  }
  if (Number(activeRoomPayload?.anomaly_id) === 68 && workType === "insight") {
    donateAnomaly68Item().catch((error) => showRuntimeErrorModal(error));
    return;
  }
  if (Number(activeRoomPayload?.anomaly_id) === 133 && workType === "intuition") {
    donateBloodbot133Hp().catch((error) => showRuntimeErrorModal(error));
    return;
  }
  selectedWorkType = workType;
  selectedRiskChoice = null;
  selectedTypeChoice = null;
  openRiskMenu();
}

async function donateAnomaly68Item() {
  const preview = await apiPost("/api/game/anomaly68-donation-preview", { user_id: currentUserId() });
  const action = preview?.action || {};
  showEventChoiceModal({
    icon: "/photo/work_room/68button.png",
    iconAlt: "Передать предмет",
    intro: action.intro || "Передать предмет",
    effect: action.effect || "Выберите предмет, который будет передан аномалии.",
    choices: [
      ...(action.items || []).map((item) => ({
        label: item.label || item.name,
        onSelect: async () => {
          const payload = await apiPost("/api/game/anomaly68-donate", {
            user_id: currentUserId(),
            slot: item.slot
          });
          closeEventModal();
          if (payload.room) renderWorkRoom(payload.room);
          await showInfoModal("Предмет передан", payload.message || "Шансы работы повышены на одну ступень.", {
            iconSrc: "/photo/work_room/68button.png",
            iconAlt: "Переданный предмет"
          });
        }
      })),
      {
        label: "Отказаться",
        onSelect: async () => closeEventModal()
      }
    ]
  });
}

async function donateBloodbot133Hp() {
  const preview = await apiPost("/api/game/bloodbot133-preview", { user_id: currentUserId(), anomaly_id: 133 });
  if (!preview.pending) {
    await showInfoModal(preview.intro || "Пожертвовать кровь", preview.effect || "Механизм уже разрушен.", {
      iconSrc: "/photo/work_room/133button.png", iconAlt: "Механизм"
    });
    return;
  }
  showEventChoiceModal({
    icon: "/photo/work_room/133button.png",
    iconAlt: "Пожертвовать кровь",
    intro: preview.intro || "Пожертвовать кровь",
    effect: `${preview.effect || "Выберите объём пожертвования."}\nТекущее HP механизма: ${Number(preview.machine_hp || 0)}.`,
    choices: [
      ...(preview.choices || []).map((choice) => ({
        label: choice.label,
        onSelect: async () => {
          try {
            const payload = await apiPost("/api/game/bloodbot133-donate", {
              user_id: currentUserId(), anomaly_id: 133, amount: choice.amount
            });
            closeEventModal();
            if (payload.room) renderWorkRoom(payload.room);
            await showInfoModal("Кровь принята", payload.message || "Механизм восстановлен.", {
              iconSrc: "/photo/work_room/133button.png", iconAlt: "Механизм"
            });
          } catch (error) {
            await showRuntimeErrorModal(error);
          }
        }
      })),
      { label: "Отказаться", onSelect: async () => closeEventModal() }
    ]
  });
}

async function openResetAction() {
  if (!activeRoomPayload?.special_actions?.reset?.available) {
    await showInfoModal("Особый эффект аномалии", "Сброс уже был произведен.", {
      iconSrc: "/photo/work_room/badresult.png",
      iconAlt: "Сброс"
    });
    return;
  }
  const payload = await apiPost("/api/game/special-reset-preview", {
    user_id: currentUserId()
  });
  const action = payload?.action || {};
  showEventChoiceModal({
    icon: "/photo/work_room/badresult.png",
    iconAlt: "Особый эффект аномалии",
    intro: action.intro || "Особый эффект аномалии",
    effect: action.effect || "",
    choices: [
      ...(action.targets || []).map((target) => ({
        label: target.label,
        onSelect: async () => {
          const applyPayload = await apiPost("/api/game/special-reset-apply", {
            user_id: currentUserId(),
            target_id: target.id
          });
          closeEventModal();
          if (applyPayload.room) {
            renderWorkRoom(applyPayload.room);
          }
          if (applyPayload.target_dead && sameUserId(applyPayload.target_id, currentUserId())) {
            await showDeathModal(getDeathReasonFromPayload(applyPayload));
          } else {
            await showInfoModal(
              "Сброс применён",
              applyPayload.message || "Особый эффект аномалии активирован.",
              {
                iconSrc: "/photo/work_room/badresult.png",
                iconAlt: "Сброс"
              }
            );
          }
        }
      })),
      {
        label: "Отказаться",
        onSelect: async () => {
          closeEventModal();
        }
      }
    ]
  });
}

function setRiskChoice(value) {
  selectedRiskChoice = Number(value);
  openTypeMenu();
}

function setTypeChoice(value) {
  selectedTypeChoice = Number(value);
  runWork(selectedWorkType);
}

function renderGameSelection(anomalies) {
  activeGameAnomalies = [...anomalies];
  activeGameSelectionKey = anomalies.map((item) => String(item.id)).join("|");
  drawGameSelection();
}

function drawGameSelection() {
  publishCameraState("selection");
  const anomalies = activeGameAnomalies;
  gameWaitingScreen.classList.add("hidden");
  gameSelectRow.innerHTML = anomalies.map((item, index) => `
    <article class="game-option" data-game-option="${index}" style="animation-delay:${index * 140}ms; --title-delay:${index * 140}ms">
      <div class="game-rail"></div>
      <img class="game-container" src="/photo/web_ui/contfix.png" alt="${item.name || item.id}">
      <div class="game-option-title">${item.name || item.id}${item.damage_hint ? `<br><span class="game-option-meta">${item.damage_hint}</span>` : ""}${item.artifact_hint ? `<br><span class="game-option-meta">${escapeHtml(item.artifact_hint)}</span>` : ""}</div>
    </article>
  `).join("");
  gameSelectDescription.textContent = "Выберите объект для работы";
  gameSelectRow.querySelectorAll("[data-game-option]").forEach((card, index) => {
    const item = anomalies[index];
    let hoverPlayed = false;
    card.addEventListener("mouseenter", () => {
      if (!hoverPlayed) {
        playSound("hoverContainer");
        hoverPlayed = true;
      }
      gameSelectDescription.textContent = item.description || "Описание пока отсутствует.";
    });
    card.addEventListener("mouseleave", () => {
      hoverPlayed = false;
      gameSelectDescription.textContent = "Выберите объект для работы";
    });
    card.addEventListener("click", () => {
      // Spectators may inspect anomaly descriptions by hovering the cards,
      // but only the active player is allowed to select one.
      if (spectatorMode) return;
      playSound("selectContainer");
      card.classList.add("is-leaving");
      if (Number(item?.id) === 32) {
        const [selected] = activeGameAnomalies.splice(index, 1);
        drawGameSelection();
        if (selected) {
          openWorkRoom(selected.id, { skipTransition: true }).catch((error) => showRuntimeErrorModal(error));
        }
        startSovuhZombieVn();
        return;
      }
      if (Number(item?.id) === PREDATOR_ANOMALY_ID) {
        const [selected] = activeGameAnomalies.splice(index, 1);
        drawGameSelection();
        if (selected) {
          openWorkRoom(selected.id, { skipTransition: true }).catch((error) => showRuntimeErrorModal(error));
        }
        startPredatorVn();
        return;
      }
      if (Number(item?.id) === PUPPY_ANOMALY_ID) {
        const [selected] = activeGameAnomalies.splice(index, 1);
        drawGameSelection();
        if (selected) {
          openWorkRoom(selected.id, { skipTransition: true }).catch((error) => showRuntimeErrorModal(error));
        }
        startPuppyVn();
        return;
      }
      window.setTimeout(() => {
        const [selected] = activeGameAnomalies.splice(index, 1);
        drawGameSelection();
        if (selected) {
          openWorkRoom(selected.id).catch((error) => showRuntimeErrorModal(error));
        }
      }, 520);
    });
  });
}

function publishCameraState(screen, anomalyId = null, force = false, extra = {}) {
  if (spectatorMode) return;
  if (screen !== "vn" && vnOverlay && !vnOverlay.classList.contains("hidden")) return;
  const key = `${screen}:${anomalyId || ""}`;
  if (!force && key === lastPublishedCameraKey) return;
  lastPublishedCameraKey = key;
  cameraPublishRevision += 1;
  apiPost("/api/game/camera-state", {
    user_id: currentUserId(),
    screen,
    anomaly_id: anomalyId,
    revision: cameraPublishRevision,
    ...extra
  }).catch(() => {});
}

gameDetailsHintsList?.addEventListener("scroll", () => {
  if (spectatorMode || gameDetailsScreen.classList.contains("hidden")) return;
  if (detailsScrollPublishTimer) window.clearTimeout(detailsScrollPublishTimer);
  detailsScrollPublishTimer = window.setTimeout(() => {
    const maxScroll = Math.max(0, gameDetailsHintsList.scrollHeight - gameDetailsHintsList.clientHeight);
    const ratio = maxScroll > 0 ? gameDetailsHintsList.scrollTop / maxScroll : 0;
    publishCameraState("details", activeRoomAnomalyId, true, { details_scroll_ratio: ratio });
  }, 70);
});

function publishVnCameraState(config = {}, objectScene = false) {
  if (spectatorMode) return;
  const choices = Array.isArray(config.choices)
    ? config.choices.map((choice) => ({ label: String(choice?.label || ""), disabled: Boolean(choice?.disabled) }))
    : [];
  const hotspots = Array.isArray(config.hotspots)
    ? config.hotspots.map((hotspot) => ({
        label: String(hotspot?.label || ""), left: String(hotspot?.left || "0"),
        top: String(hotspot?.top || "0"), width: String(hotspot?.width || "0"), height: String(hotspot?.height || "0")
      }))
    : [];
  publishCameraState("vn", activeRoomAnomalyId, true, {
    vn_state: {
      background: config.background || "",
      background_style: config.backgroundStyle || {},
      portrait: config.portrait || "/photo/VN/VN_anomaly.png",
      nameplate: config.nameplate === "" ? "" : (config.nameplate || config.codeName || "Аномалия"),
      speaker: config.speaker || "",
      text: String(config.text || ""),
      object_prompt: objectScene ? String(config.objectPrompt || config.text || "") : "",
      scene_time: String(config.sceneTime || ""),
      dark_scene: Boolean(config.darkScene), object_scene: Boolean(objectScene),
      character_visible: config.characterVisible !== false,
      portrait_visible: config.portraitVisible !== false,
      nameplate_visible: config.nameplateVisible !== false,
      confirm_label: config.confirmOnly ? String(config.confirmLabel || "ОК") : "",
      input_placeholder: config.input ? String(config.input.placeholder || "") : "",
      choices, hotspots,
    }
  });
}

function publishCurrentVnDomState(popupText = "", popupChoices = []) {
  if (spectatorMode || !vnOverlay || vnOverlay.classList.contains("hidden")) return;
  const sceneTime = vnWindow?.querySelector(".vn-scene-time");
  publishCameraState("vn", activeRoomAnomalyId, true, {
    vn_state: {
      background: vnBg && !vnBg.classList.contains("hidden") ? (vnBg.getAttribute("src") || "") : "",
      background_style: vnBg ? { objectFit: vnBg.style.objectFit, width: vnBg.style.width, height: vnBg.style.height, left: vnBg.style.left, top: vnBg.style.top } : {},
      portrait: vnPortrait?.getAttribute("src") || "/photo/VN/VN_anomaly.png",
      nameplate: vnNameplate?.textContent || "", speaker: vnSpeaker?.textContent || "",
      text: vnText?.textContent || "", object_prompt: vnObjectPrompt?.textContent || "",
      scene_time: sceneTime?.textContent || "",
      dark_scene: vnWindow?.classList.contains("dark-scene"),
      object_scene: vnWindow?.classList.contains("object-scene"),
      character_visible: !vnWindow?.classList.contains("character-hidden"),
      portrait_visible: !vnWindow?.classList.contains("portrait-hidden"),
      nameplate_visible: !vnWindow?.classList.contains("nameplate-hidden"),
      confirm_label: vnCloseButton && !vnCloseButton.classList.contains("hidden") ? vnCloseButton.textContent : "",
      input_placeholder: vnChoices?.querySelector(".vn-dialog-input")?.placeholder || "",
      choices: Array.from(vnChoices?.querySelectorAll(".vn-choice-button") || []).map((button) => ({ label: button.textContent || "", disabled: true })),
      hotspots: Array.from(vnHotspots?.querySelectorAll(".vn-hotspot") || []).map((button) => ({
        label: button.textContent || "", left: button.style.left, top: button.style.top,
        width: button.style.width, height: button.style.height
      })),
      popup_text: String(popupText || ""),
      popup_choices: (popupChoices || []).map((label) => String(label || "")),
    }
  });
}

function renderSpectatorVn(state = {}) {
  if (!vnOverlay || !vnWindow) return;
  spectatorVnVisible = true;
  vnWindow.classList.toggle("object-scene", Boolean(state.object_scene));
  vnWindow.classList.toggle("dark-scene", Boolean(state.dark_scene));
  vnWindow.classList.toggle("character-hidden", state.character_visible === false);
  vnWindow.classList.toggle("portrait-hidden", state.portrait_visible === false);
  vnWindow.classList.toggle("nameplate-hidden", state.nameplate_visible === false);
  vnNameplate.textContent = state.nameplate || "";
  vnSpeaker.textContent = state.speaker || "";
  vnPortrait.src = state.portrait || "/photo/VN/VN_anomaly.png";
  vnPortrait.alt = state.speaker || "Персонаж";
  if (state.background) {
    vnBg.classList.remove("hidden");
    vnBg.src = state.background;
    vnBg.style.objectFit = state.background_style?.objectFit || "cover";
    vnBg.style.width = state.background_style?.width || "100%";
    vnBg.style.height = state.background_style?.height || "100%";
    vnBg.style.left = state.background_style?.left || "0";
    vnBg.style.top = state.background_style?.top || "0";
  } else {
    vnBg.classList.add("hidden");
    vnBg.removeAttribute("src");
  }
  vnText.textContent = state.object_scene ? "" : String(state.text || "");
  vnObjectPrompt.textContent = String(state.object_prompt || "");
  vnObjectPrompt.classList.toggle("hidden", !state.object_prompt);
  vnChoices.innerHTML = "";
  if (state.input_placeholder) {
    const input = document.createElement("input");
    input.className = "vn-dialog-input";
    input.placeholder = state.input_placeholder;
    input.disabled = true;
    vnChoices.appendChild(input);
  }
  (state.choices || []).forEach((choice) => {
    const button = document.createElement("button");
    button.className = "vn-choice-button disabled";
    button.disabled = true;
    button.textContent = choice.label || "";
    vnChoices.appendChild(button);
  });
  vnHotspots.innerHTML = "";
  (state.hotspots || []).forEach((hotspot) => {
    const button = document.createElement("button");
    button.className = "vn-hotspot";
    button.disabled = true;
    button.style.left = hotspot.left; button.style.top = hotspot.top;
    button.style.width = hotspot.width; button.style.height = hotspot.height;
    const label = document.createElement("span"); label.textContent = hotspot.label || "";
    button.appendChild(label); vnHotspots.appendChild(button);
  });
  let sceneTime = vnWindow.querySelector(".vn-scene-time");
  if (!sceneTime) { sceneTime = document.createElement("div"); sceneTime.className = "vn-scene-time"; vnWindow.appendChild(sceneTime); }
  sceneTime.textContent = state.scene_time || "";
  sceneTime.classList.toggle("hidden", !state.scene_time);
  vnCloseButton.textContent = state.confirm_label || "ОК";
  vnCloseButton.classList.toggle("hidden", !state.confirm_label);
  vnCloseButton.disabled = true;
  if (state.popup_text) {
    vnPopupText.textContent = state.popup_text;
    vnPopupActions.innerHTML = "";
    (state.popup_choices || []).forEach((labelText) => {
      const button = document.createElement("button");
      button.className = "vn-choice-button disabled";
      button.disabled = true;
      button.textContent = labelText;
      vnPopupActions.appendChild(button);
    });
    vnPopup.classList.remove("hidden");
  } else {
    vnPopup?.classList.add("hidden");
  }
  vnOverlay.classList.remove("hidden");
}

function hideSpectatorVn() {
  if (!spectatorVnVisible) return;
  spectatorVnVisible = false;
  vnOverlay?.classList.add("hidden");
  if (vnCloseButton) vnCloseButton.disabled = false;
}

function renderGameActionLog(entries = []) {
  if (!gameActionLog) return;
  const visibleEntries = Array.isArray(entries) ? entries.slice(-10) : [];
  gameActionLog.classList.toggle("hidden", visibleEntries.length === 0);
  gameActionLog.innerHTML = visibleEntries.map((entry) => (
    `<div class="game-action-log-entry ${entry?.kind === "effect" ? "effect" : "work"}">${escapeHtml(entry?.text || "")}</div>`
  )).join("");
}

function stopSpectatorCamera() {
  hideSpectatorVn();
  const emojiSpectatorOverlay = document.getElementById("emojiGlassesOverlay");
  const seaSpectatorOverlay = document.getElementById("seaMonsterOverlay");
  if (emojiSpectatorOverlay?.classList.contains("spectator-copy")) emojiSpectatorOverlay.classList.add("hidden");
  if (seaSpectatorOverlay?.classList.contains("spectator-copy")) seaSpectatorOverlay.classList.add("hidden");
  spectatorMode = false;
  spectatorCameraKey = "";
  gameScreen.classList.remove("spectator-camera");
  spectatorCameraOverlay?.classList.add("hidden");
  if (spectatorNoiseTimer) window.clearTimeout(spectatorNoiseTimer);
  spectatorNoiseTimer = null;
}

function scheduleSpectatorNoise() {
  if (!spectatorMode || !spectatorCameraOverlay) return;
  if (spectatorNoiseTimer) window.clearTimeout(spectatorNoiseTimer);
  spectatorNoiseTimer = window.setTimeout(() => {
    if (!spectatorMode) return;
    spectatorCameraOverlay.classList.add("is-interfering");
    window.setTimeout(() => spectatorCameraOverlay.classList.remove("is-interfering"), 520);
    scheduleSpectatorNoise();
  }, 6500 + Math.random() * 11500);
}

async function showSpectatorCamera(camera = {}) {
  spectatorMode = true;
  gameScreen.classList.add("spectator-camera");
  spectatorCameraOverlay?.classList.remove("hidden");
  if (spectatorCameraName) spectatorCameraName.textContent = camera.player_name || "—";
  if (!spectatorNoiseTimer) scheduleSpectatorNoise();
  // Render the camera behind local dialogs as well. The dialog remains on top
  // until its own OK button is pressed, while the dead player never sees an
  // empty black layer underneath it.
  const screen = camera.screen || "selection";
  const anomalyId = Number(camera.anomaly_id || 0);
  const key = `${camera.player_id || 0}:${screen}:${anomalyId}:${camera.revision || 0}:${(camera.anomalies || []).map(item => item.id).join(",")}`;
  if (key === spectatorCameraKey) return;
  spectatorCameraKey = key;
  gameWaitingScreen.classList.add("hidden");
  if (screen !== "emoji_game") document.getElementById("emojiGlassesOverlay")?.classList.add("hidden");
  if (screen !== "sea_game") document.getElementById("seaMonsterOverlay")?.classList.add("hidden");
  try {
    if (screen === "emoji_game") {
      hideSpectatorVn();
      renderSpectatorEmojiGame(camera.mini_game_state || {});
      gameSelectScreen.classList.add("hidden");
      gameRoomScreen.classList.add("hidden");
      gameDetailsScreen.classList.add("hidden");
    } else if (screen === "sea_game") {
      hideSpectatorVn();
      renderSpectatorSeaGame(camera.mini_game_state || {});
      gameSelectScreen.classList.add("hidden");
      gameRoomScreen.classList.add("hidden");
      gameDetailsScreen.classList.add("hidden");
    } else if (screen === "vn") {
      renderSpectatorVn(camera.vn_state || {});
      gameSelectScreen.classList.add("hidden");
      gameRoomScreen.classList.add("hidden");
      gameDetailsScreen.classList.add("hidden");
    } else if (screen === "room" && anomalyId) {
      hideSpectatorVn();
      const payload = await api(`/api/work-room?user_id=${encodeURIComponent(String(camera.player_id))}&anomaly_id=${anomalyId}&observe=1`);
      renderWorkRoom(payload.room);
      gameDetailsScreen.classList.add("hidden");
    } else if (screen === "details" && anomalyId) {
      hideSpectatorVn();
      const payload = await api(`/api/details?user_id=${encodeURIComponent(String(camera.player_id))}&anomaly_id=${anomalyId}`);
      activeRoomAnomalyId = anomalyId;
      renderDetailsScreen(payload.details);
      gameSelectScreen.classList.add("hidden");
      gameRoomScreen.classList.add("hidden");
      gameDetailsScreen.classList.remove("hidden");
      window.requestAnimationFrame(() => {
        const ratio = Math.max(0, Math.min(1, Number(camera.details_scroll_ratio || 0)));
        const maxScroll = Math.max(0, gameDetailsHintsList.scrollHeight - gameDetailsHintsList.clientHeight);
        gameDetailsHintsList.scrollTop = maxScroll * ratio;
      });
    } else {
      hideSpectatorVn();
      renderGameSelection(Array.isArray(camera.anomalies) ? camera.anomalies : []);
      gameSelectScreen.classList.remove("hidden");
      gameRoomScreen.classList.add("hidden");
      gameDetailsScreen.classList.add("hidden");
    }
  } catch (_) {
    showWaitingState({});
  }
}

function showWaitingState(turnUi = {}) {
  gameSelectScreen.classList.add("hidden");
  gameRoomScreen.classList.add("hidden");
  gameDetailsScreen.classList.add("hidden");
  gameWaitingScreen.classList.remove("hidden");
  stopGameMusic();
  renderTurnRibbon(turnUi);
}

async function handleD20CurseRoll() {
  if (d20RollInFlight) return true;
  d20RollInFlight = true;
  try {
    const result = await apiPost("/api/game/d20-roll", { user_id: currentUserId() });
    applyDamageFeedback(result);
    await showInfoModal(
      `Проклятый кубик: ${Number(result.roll || 0)}`,
      result.text || "Кубик закончил бросок.",
      { iconSrc: "/photo/anomaly/043_d20.png", iconAlt: "Двадцатигранный кубик" }
    );
    if (result.damage?.shield_triggered) await showDeathShieldMiracleModal(result.damage);
    if (result.player_dead) {
      await showDeathModal(result.death_reason || "Погиб от проклятия двадцатигранного кубика");
      if (showFinalResults(result.final_results || result.game_state?.final_results)) return true;
      if (result.game_state?.game?.started) await applyGameState(result.game_state, { forceRefresh: true, skipD20: true });
      return true;
    }
    if (result.game_state?.game?.started) {
      await applyGameState(result.game_state, { skipD20: true });
    }
    return true;
  } finally {
    d20RollInFlight = false;
  }
}

async function handleCrimsonBite(prompt = {}) {
  if (!prompt?.pending) return false;
  if (crimsonBiteResolving) return true;
  const targets = Array.isArray(prompt.targets) ? prompt.targets : [];
  const resolveBite = async (targetId = null) => {
    if (crimsonBiteResolving) return;
    crimsonBiteResolving = true;
    try {
      const result = await apiPost("/api/game/crimson-bite", {
        user_id: currentUserId(),
        target_id: targetId
      });
      closeEventModal();
      if (result.player_dead) {
        await showDeathModal(result.death_reason || "Голод Багрового вируса свёл с ума");
        if (showFinalResults(result.final_results || result.game_state?.final_results)) return;
      } else {
        await showInfoModal(
          result.kind === "bite" ? "Голод утолён" : "Голод сводит с ума...",
          result.message || "Багровый вирус требует крови.",
          { iconSrc: "/photo/work_room/badresult.png", iconAlt: "Багровый вирус" }
        );
      }
      if (result.game_state?.game?.started) {
        await applyGameState(result.game_state, { forceRefresh: true, skipCrimson: true });
      }
    } catch (error) {
      closeEventModal();
      await showRuntimeErrorModal(error);
    } finally {
      crimsonBiteResolving = false;
    }
  };
  if (!targets.length) {
    await resolveBite(null);
    return true;
  }
  if (eventOverlay && !eventOverlay.classList.contains("hidden")) return true;
  showEventChoiceModal({
    intro: "Багровый голод",
    effect: "Выберите другую живую цель для укуса.",
    icon: "/photo/work_room/badresult.png",
    iconAlt: "Багровый вирус",
    choices: targets.map((target) => ({
      label: `Укусить ${target.label}`,
      onSelect: async () => resolveBite(String(target.id))
    }))
  });
  return true;
}

function updateTrainDebugTimer(ticket = {}) {
  if (!gameRoomGlobals || !debugModeEnabled) return;
  const lines = String(gameRoomGlobals.textContent || "GLOBALS").split("\n").filter((line) => !line.startsWith("TrainTimer = "));
  if (!ticket?.active) {
    gameRoomGlobals.textContent = lines.join("\n");
    return;
  }
  const remaining = Math.max(0, Math.ceil(Number(ticket.deadline_at || 0) - Date.now() / 1000));
  const minutes = String(Math.floor(remaining / 60)).padStart(2, "0");
  const seconds = String(remaining % 60).padStart(2, "0");
  const timerLine = `TrainTimer = ${minutes}:${seconds}${ticket.paused ? " (пауза VN)" : ""}`;
  lines.splice(1, 0, timerLine);
  gameRoomGlobals.textContent = lines.join("\n");
}

async function handleTrainTicketState(ticket = {}) {
  currentTrainTicketState = ticket || {};
  const vnActive = vnOverlay && !vnOverlay.classList.contains("hidden");
  if (trainTicketButton) {
    trainTicketButton.classList.toggle("hidden", !ticket?.active || ticket?.paused || vnActive);
    trainTicketButton.classList.remove("train-time-3", "train-time-2", "train-time-1");
    if (ticket?.active && ticket?.deadline_at) {
      const remaining = Math.max(0, Math.ceil(Number(ticket.deadline_at) - Date.now() / 1000));
      trainTicketButton.classList.add(remaining > 120 ? "train-time-3" : remaining > 60 ? "train-time-2" : "train-time-1");
    }
  }
  updateTrainDebugTimer(ticket);
  const event = ticket?.event;
  if (!event?.id) return;
  const storageKey = `train-event:${currentUserId()}`;
  if (window.sessionStorage.getItem(storageKey) === String(event.id)) return;
  window.sessionStorage.setItem(storageKey, String(event.id));
  playSound("trainEnd");
  if (trainDamageFlash) {
    trainDamageFlash.classList.remove("active");
    void trainDamageFlash.offsetWidth;
    trainDamageFlash.classList.add("active");
    window.setTimeout(() => trainDamageFlash.classList.remove("active"), 700);
  }
  if (event.player_dead) {
    await showDeathModal(event.death_reason || "Был раздавлен адским экспрессом");
  } else {
    showInfoToast("Адский экспресс прибыл и нанёс 200 урона!");
  }
}

function handleViolinButtonState(state = {}) {
  if (!violinStealButton) return;
  const vnActive = vnOverlay && !vnOverlay.classList.contains("hidden");
  const tennaActive = tennaOverlay && !tennaOverlay.classList.contains("hidden");
  violinStealButton.classList.toggle("hidden", !state?.visible || vnActive || tennaActive);
  violinStealButton.title = state?.visible
    ? `Украсть скрипку — текущая сила волны ${Number(state.damage || 40)}`
    : "Украсть Скрипку Безмолвного Дирижёра";
}

async function handleBrassSphereEvent(event = null) {
  if (!event?.id) return;
  const storageKey = `brass-sphere-event:${currentUserId()}`;
  if (window.sessionStorage.getItem(storageKey) === String(event.id)) return;
  window.sessionStorage.setItem(storageKey, String(event.id));
  playSound("damageHit");
  triggerDamageFlash();
  if (event.player_dead) {
    await showDeathModal(event.death_reason || "Был поглощён металлическим шаром из латуни");
  }
}

async function handleX125Events(events = []) {
  const ordered = Array.isArray(events) ? events : [];
  for (const event of ordered) {
    const eventId = Number(event?.id || 0);
    if (!eventId) continue;
    const runId = Number(event?.run_token || event?.run_id || 1);
    const storageKey = `x125-last-event:${runId}`;
    const lastSeen = Number(window.localStorage.getItem(storageKey) || 0);
    if (eventId <= lastSeen) continue;
    window.localStorage.setItem(storageKey, String(eventId));
    playSound("tickOfDoom");
    await enqueueSystemEventModal(() => showInfoModal(
      "Х-125",
      event.text || `Счетчик аномалии Х-125 достиг значения ${Number(event.remaining || 0)} из-за ${event.reason || "неизвестного действия"}.`,
      { iconSrc: "/photo/work_room/neutralresult.png", iconAlt: "Х-125" }
    ));
  }
}

function waitX125Intro(ms) {
  return new Promise(resolve=>window.setTimeout(resolve,ms));
}

function playX125IntroClip(source,maxMs=5000) {
  return new Promise(resolve=>{
    const audio=source.cloneNode(),finish=()=>{window.clearTimeout(timer);audio.removeEventListener("ended",finish);resolve();};
    audio.volume=source.volume;
    audio.addEventListener("ended",finish,{once:true});
    const timer=window.setTimeout(finish,maxMs);
    audio.play().catch(()=>{});
  });
}

async function playX125EramIntro(event) {
  const overlay=document.createElement("div");
  overlay.className="x125-eram-intro";
  overlay.innerHTML=`<div class="x125-eram-stage"><img src="/photo/special/eram1.png" alt="Эрам"><div class="x125-eram-line"></div></div>`;
  document.body.appendChild(overlay);
  const stage=overlay.querySelector(".x125-eram-stage"),line=overlay.querySelector(".x125-eram-line");
  const resumeBackground=Boolean(gameMusic&&!gameMusic.paused&&backgroundMusicEnabled);
  x125AudioLock=true;
  if(gameMusic)gameMusic.pause();
  await waitX125Intro(1000);
  await playX125IntroClip(soundPlayers.imageFriendLaugh,6500);
  stage.classList.add("visible");
  await waitX125Intro(800);
  const name=String(event?.player_name||"СОТРУДНИК").trim()||"СОТРУДНИК";
  const lines=[
    "ТАК ВОТ КТО МЕНЯ ПРОБУДИЛ",
    `...${name}`,
    "РАЗ УЖ Я НЕ СПЛЮ, ТО НАВЕРНОЕ СТОИТ НАГРАДИТЬ ТЕБЯ ЗА ТВОИ СТАРАНИЯ. ВСЕ ТАКИ ТЫ ПРИЛОЖИЛ НЕМАЛО УСИЛИЙ",
    "Я ЗНАЮ ТАКИХ КАК ТЫ. ВСЕ ВЫ ИЩЕТЕ КОНТЕНТ",
    "В ТАКОМ СЛУЧАЕ Я ДАМ ТЕБЕ ТО, ЧТО ТЫ ХОЧЕШЬ"
  ];
  for(const text of lines){
    line.classList.remove("shown");
    await waitX125Intro(160);
    line.textContent=text;
    line.classList.add("shown");
    const voice=playX125IntroClip(soundPlayers.eramLaugh,2200);
    await Promise.all([voice,waitX125Intro(Math.max(2200,Math.min(4800,1200+text.length*32)))]);
  }
  line.classList.remove("shown");
  stage.classList.add("leaving");
  await playX125IntroClip(soundPlayers.imageFriendLaugh,6500);
  overlay.classList.add("leaving");
  await waitX125Intro(700);
  overlay.remove();
  return resumeBackground;
}

async function playX125EramOutro(rewardCp) {
  const overlay=document.createElement("div");
  overlay.className="x125-eram-intro";
  overlay.innerHTML=`<div class="x125-eram-stage visible"><img src="/photo/special/eram1.png" alt="Эрам"><div class="x125-eram-line"></div></div>`;
  document.body.appendChild(overlay);
  const stage=overlay.querySelector(".x125-eram-stage"),line=overlay.querySelector(".x125-eram-line");
  const lines=[
    "ТАК ТЕБЕ УДАЛОСЬ ВЫЖИТЬ",
    "ПОХВАЛЬНО",
    "ПРИХОДИ ПОИГРАТЬ ЕЩЕ",
    `А ЭТО ТЕБЕ ЗА ТО ЧТО ПОВЕСЕЛИЛ МЕНЯ, ТВОЯ НАГРАДА - \nНАЧИСЛЕНО ${Math.max(0,Number(rewardCp||0))} СО`
  ];
  await playX125IntroClip(soundPlayers.imageFriendLaugh,5000);
  for(const text of lines){
    line.classList.remove("shown");
    await waitX125Intro(160);
    line.textContent=text;
    line.classList.add("shown");
    await Promise.all([playX125IntroClip(soundPlayers.eramLaugh,2200),waitX125Intro(Math.max(2200,Math.min(4400,1200+text.length*32)))]);
  }
  line.classList.remove("shown");
  stage.classList.add("leaving");
  await playX125IntroClip(soundPlayers.imageFriendLaugh,5000);
  overlay.classList.add("leaving");
  await waitX125Intro(700);
  overlay.remove();
}

async function playX125DeadOwnerMonologue(event) {
  const overlay=document.createElement("div");
  overlay.className="x125-eram-intro";
  overlay.innerHTML=`<div class="x125-eram-stage visible"><img src="/photo/special/eram1.png" alt="Эрам"><div class="x125-eram-line"></div></div>`;
  document.body.appendChild(overlay);
  const stage=overlay.querySelector(".x125-eram-stage"),line=overlay.querySelector(".x125-eram-line");
  const owner=event?.battle?.owner_name||event?.player_name||"Сотрудник";
  const lines=[
    `Я ПРОБУДИЛСЯ, БЛАГОДАРЯ ${owner}`,
    "НО ГДЕ ОН? МЕРТВ?",
    "ХММ... В ТАКОМ СЛУЧАЕ ПОИГРАТЬ НЕ ПОЛУЧИТСЯ",
    "ТОГДА РАЗВЛЕКУСЬ В КОМПЛЕКСЕ ТАК, ЧТО НИКТО НЕ ЗАБУДЕТ. ХИ-ХИ-ХИ"
  ];
  await playX125IntroClip(soundPlayers.imageFriendLaugh,5000);
  for(const text of lines){
    line.classList.remove("shown");
    await waitX125Intro(160);
    line.textContent=text;
    line.classList.add("shown");
    await Promise.all([playX125IntroClip(soundPlayers.eramLaugh,2200),waitX125Intro(Math.max(2200,Math.min(5000,1200+text.length*32)))]);
  }
  line.classList.remove("shown");
  stage.classList.add("leaving");
  await playX125IntroClip(soundPlayers.imageFriendLaugh,5000);
  overlay.classList.add("leaving");
  await waitX125Intro(700);
  overlay.remove();
}

function ensureFullscreenEventOverlay() {
  let overlay = document.getElementById("fullscreenEventOverlay");
  if (overlay) return overlay;
  overlay = document.createElement("div");
  overlay.id = "fullscreenEventOverlay";
  overlay.className = "fullscreen-event-overlay hidden";
  overlay.innerHTML = `
    <img class="fullscreen-event-image hidden" alt="Событие">
    <div class="fullscreen-event-message hidden">
      <div class="fullscreen-event-title"></div>
      <div class="fullscreen-event-text"></div>
      <button class="fullscreen-event-ok" type="button">ОК</button>
    </div>`;
  document.body.appendChild(overlay);
  return overlay;
}

function showFullscreenEventMessage(title, message) {
  const overlay = ensureFullscreenEventOverlay();
  const image = overlay.querySelector(".fullscreen-event-image");
  const card = overlay.querySelector(".fullscreen-event-message");
  image.classList.add("hidden");
  card.classList.remove("hidden");
  overlay.querySelector(".fullscreen-event-title").textContent = title || "Событие";
  overlay.querySelector(".fullscreen-event-text").textContent = message || "";
  overlay.classList.remove("hidden");
  return new Promise((resolve) => {
    const button = overlay.querySelector(".fullscreen-event-ok");
    button.onclick = () => {
      overlay.classList.add("hidden");
      card.classList.add("hidden");
      resolve();
    };
  });
}

async function handleX125SpecialEvent(event = null) {
  const eventId = Number(event?.id || 0);
  if (!eventId) return;
  // Propagate terminal states to an already-open battle as well. Previously
  // only an active state was copied, so observers kept rendering after death.
  if (x125BattleRuntime && event?.battle) {
    x125BattleRuntime.serverState = event.battle;
  }
  if(event?.battle?.status === "owner_dead_intro"){
    const key=`x125-dead-owner-intro:${eventId}`;
    if(window.localStorage.getItem(key)!=="shown"){
      window.localStorage.setItem(key,"shown");
      await playX125DeadOwnerMonologue(event);
    }
    try{
      const payload=await apiPost("/api/game/x125-dead-owner-finish",{user_id:currentUserId()});
      if(showFinalResults(payload.final_results||payload.game_state?.final_results))return;
      if(payload.game_state)await applyGameState(payload.game_state,{forceRefresh:true});
    }catch(error){showRuntimeErrorModal(error);}
    return;
  }
  if (event?.battle?.status === "active") {
    if (x125BattleRuntime) {
      x125BattleRuntime.serverState = event.battle;
      return;
    }
    const eventId=Number(event?.id||event?.battle?.id||0);
    if(eventId&&window.localStorage.getItem(`x125-battle-finished:${eventId}`)==="yes")return;
    x125PendingIntroEvent=event;
    if(x125IntroActive)return;
    x125IntroActive=true;
    try{
      const introKey=`x125-intro-shown:${eventId}`;
      let resumeBackground=Boolean(gameMusic&&!gameMusic.paused&&backgroundMusicEnabled);
      if(!eventId||window.localStorage.getItem(introKey)!=="yes"){
        if(eventId)window.localStorage.setItem(introKey,"yes");
        resumeBackground=await playX125EramIntro(x125PendingIntroEvent);
      }
      let battle=x125PendingIntroEvent?.battle||event.battle;
      if(sameUserId(battle?.owner_id,currentUserId())){
        try{const payload=await apiPost("/api/game/x125-battle-update",{user_id:currentUserId(),state:{restart_attack:1}});battle=payload.battle||battle;}catch(_){}
      }
      if(battle?.status==="active"&&!x125BattleRuntime)startX125SoulBattle(battle,resumeBackground);
    }finally{x125IntroActive=false;x125PendingIntroEvent=null;}
    return;
  }
  const storageKey = `x125-special-event:${eventId}`;
  if (["completed", "dead"].includes(event?.battle?.status)) {
    window.localStorage.setItem(storageKey, "shown");
    return;
  }
  if (window.localStorage.getItem(storageKey) === "shown") return;
  window.localStorage.setItem(storageKey, "shown");
  await showFullscreenEventMessage(event.title || "Х-125", event.text || "Особое событие Х-125.");
}

function x125Hash(index, salt = 0) {
  const value = Math.sin((index + 1) * 91.733 + salt * 17.117) * 43758.5453;
  return value - Math.floor(value);
}

const X125_WAVES = [["attack1.lua", 8.25], ["attack2.lua", 8.0], ["yellow1.lua", 11.0], ["yellow2.lua", 30.0], ["orangetraps.lua", 12.0], ["spaceinvaders.lua", 90.0], ["circlemadness.lua", 15.0], ["piano1.lua", 17.75], ["timeflow1.lua", 15.0], ["final.lua", 90.0]];
const X125_WAVE_GAP = 0.8;
const X125_BATTLE_LENGTH = X125_WAVES.reduce((sum, wave) => sum + wave[1], 0) + Math.max(0, X125_WAVES.length - 1) * X125_WAVE_GAP;
const x125ImageCache = new Map();

function x125Image(path) {
  if (!x125ImageCache.has(path)) { const img = new Image(); img.src = `/photo/x_125/${path}`; x125ImageCache.set(path, img); }
  return x125ImageCache.get(path);
}

function x125GasterSize(size) {
  return size === 2 ? { headW:86, headH:269, beam:128 } : size === 1 ? { headW:32, headH:100, beam:32 } : { headW:43, headH:134, beam:64 };
}

function x125GasterVisible(luaX, luaY) {
  const canvasY=480-luaY;
  return luaX>=0&&luaX<=640&&canvasY>=0&&canvasY<=480;
}

function x125GasterBeam(id, luaX, luaY, rotation, size, dangerous, color="#fff") {
  const dimensions=x125GasterSize(size),largeOffset=size===2?60:0;
  let x=luaX,y=480-luaY,w=dimensions.beam,h=1500,axis="v";
  if(rotation===0)y=480-(luaY-690-largeOffset);
  else if(rotation===180)y=480-(luaY+690+largeOffset);
  else {axis="h";w=1500;h=dimensions.beam;if(rotation===90)x=luaX-690-largeOffset;else x=luaX+690+largeOffset;}
  const canvasHeadY=480-luaY,muzzle=Math.max(12,dimensions.headH*.38);let hitX=luaX,hitY=canvasHeadY,hitW=dimensions.beam,hitH=dimensions.beam;
  if(rotation===0){hitY=(canvasHeadY+muzzle+480)/2;hitH=Math.max(0,480-(canvasHeadY+muzzle));}
  else if(rotation===180){hitY=Math.max(0,canvasHeadY-muzzle)/2;hitH=Math.max(0,canvasHeadY-muzzle);}
  else if(rotation===90){hitX=Math.max(0,luaX-muzzle)/2;hitW=Math.max(0,luaX-muzzle);}
  else {hitX=(luaX+muzzle+640)/2;hitW=Math.max(0,640-(luaX+muzzle));}
  return {id,x,y,w,h,hitX,hitY,hitW,hitH,r:dimensions.beam/2,shape:"laser",sprite:`laser${size}/laser${axis}4.png`,color,dangerous};
}

function x125LaserBotParts(id, luaX, luaY, rotation, color, frame=0) {
  const blue=color==="blue",tint=blue?"#4ba9ff":"#ff8a38";
  let x=luaX,y=480-luaY,w=6,h=480,axis="v";
  if(rotation===0)y=480-(luaY-253);
  else if(rotation===180)y=480-(luaY+251);
  else {axis="h";w=640;h=6;if(rotation===90)x=luaX-333;else x=luaX+331;}
  const headY=480-luaY,muzzle=22;let hitX=luaX,hitY=headY,hitW=6,hitH=6;
  if(rotation===0){hitY=(headY+muzzle+480)/2;hitH=Math.max(0,480-(headY+muzzle));}
  else if(rotation===180){hitY=Math.max(0,headY-muzzle)/2;hitH=Math.max(0,headY-muzzle);}
  else if(rotation===90){hitX=Math.max(0,luaX-muzzle)/2;hitW=Math.max(0,luaX-muzzle);}
  else {hitX=(luaX+muzzle+640)/2;hitW=Math.max(0,640-(luaX+muzzle));}
  return [
    {id:`${id}-body`,x:luaX,y:480-luaY,w:56,h:56,r:28,shape:"sprite",sprite:`bot${rotation}/spr_lasermachine_${blue?"b":"o"}_${frame}.png`,dangerous:false},
    {id:`${id}-beam`,x,y,w,h,hitX,hitY,hitW,hitH,r:3,shape:"laser",sprite:`bolasers/${blue?"b":"o"}laser6${axis}.png`,color:tint,dangerous:true}
  ];
}

function x125Timeline(elapsed) {
  let cursor = 0;
  for (let i = 0; i < X125_WAVES.length; i += 1) {
    const duration = X125_WAVES[i][1];
    const gap = i < X125_WAVES.length - 1 ? X125_WAVE_GAP : 0;
    if (elapsed < cursor + duration + gap) return { attack:i + 1, name:X125_WAVES[i][0], time:Math.max(0, elapsed - cursor), active:elapsed < cursor + duration };
    cursor += duration + X125_WAVE_GAP;
  }
  const last = X125_WAVES.length - 1;
  return { attack:last + 1, name:X125_WAVES[last][0], time:X125_WAVES[last][1], active:false };
}

function x125SourceHazards(attack, t, arena) {
  const out=[]; const push=(x,y,r,color="#fff",shootable=false,shape="circle",w=r*2,h=r*2,sprite="")=>out.push({x,y,r,color,shootable,shape,w,h,sprite});
  const laser=(side,pos,start,width=13,length=arena.w)=>{const age=t-start;if(age<0||age>1.55)return;const firing=age>.72&&age<1.32;let x=arena.x+arena.w/2,y=arena.y+arena.h/2,w=width,h=width;if(side==="h"){y=pos;w=length;}else{x=pos;h=arena.h;}push(x,y,width/2,firing?"#fff":"rgba(255,255,255,.2)",false,"laser",w,h,"gaster0/gb0.png");out[out.length-1].dangerous=firing;};
  if(attack===1){[["h",arena.y+45,.2],["v",arena.x+105,.2],["h",arena.y+arena.h-50,1.5],["v",arena.x+arena.w-110,1.5],["h",arena.y+90,2.8],["v",arena.x+arena.w/2,4.1],["h",arena.y+arena.h-85,5.4]].forEach(v=>laser(...v,18));for(let i=0;i<8;i++){const x=arena.x+arena.w+70-((t-3.4)*220+i*88);if(t>3.4)push(x,arena.y+arena.h-45,13,i%2?"#4ba9ff":"#ff8a38",false,"rect",26,18,"bot0/spr_lasermachine_off_0.png");}}
  else if(attack===2){for(let i=0;i<4;i++){laser("h",arena.y+45+i*95,.2+i*.5,i%2?10:18);laser("v",arena.x+55+i*175,.7+i*.5,i%2?10:18);}for(let i=0;i<7;i++){const p=(t*155+i*90)%(arena.w+100);push(arena.x+p-50,arena.y+45+(i%4)*92,11,"#4ba9ff",false,"rect",25,17,"bot0/spr_lasermachine_b_0.png");}}
  else if(attack===3){for(let row=0;row<3;row++)for(let col=0;col<7;col++){const y=arena.y+arena.h+45-(t*145-row*26);push(arena.x+65+col*85,y,12,"#d8d8d8",true,"rect",22,22,"sbox/sbox.png");}for(let i=0;i<7;i++){const y=arena.y+arena.h+100-(t-2.2)*70;push(arena.x+70+i*82,y,15,"#ffce35",true,"rect",28,28,"plus/plus0.png");}if(t>3.6)for(let i=0;i<5;i++)push(arena.x+100+i*110,arena.y+45+Math.sin(t*2+i)*25,18,"#ff6688",true,"rect",34,34,"para/para0.png");}
  else if(attack===4){for(let ring=0;ring<3;ring++)for(let i=0;i<10;i++){const a=i*Math.PI/5+t*(1.2+ring*.45)*(ring%2?-1:1),d=65+ring*70;push(arena.x+arena.w/2+Math.cos(a)*d,arena.y+arena.h/2+Math.sin(a)*d,8,"#7ee8ff",false,"rect",14,24,"bolt.png");}for(let i=0;i<7;i++){const a=i*Math.PI*2/7-t;push(arena.x+arena.w/2+Math.cos(a)*140,arena.y+arena.h/2+Math.sin(a)*140,12,"#ddd",true,"rect",22,22,"sbox/sbox.png");}}
  else if(attack===5){for(let i=0;i<10;i++){const x=arena.x+80+i*(arena.w-160)/9;push(x,arena.y+arena.h*.55,9,"#ff8a38",false,"laser",8,arena.h*.75,"bot0/spr_lasermachine_o_0.png");}[["v",arena.x+arena.w/2,.2],["h",arena.y+70,.82],["h",arena.y+arena.h-70,1.4],["v",arena.x+140,4],["v",arena.x+arena.w-140,4],["h",arena.y+arena.h/2,6],["h",arena.y+100,9.7],["h",arena.y+arena.h-100,9.7]].forEach(v=>laser(...v,16));}
  else if(attack===6){const sway=Math.sin(t*.8)*55;for(let row=0;row<3;row++)for(let col=0;col<7;col++){push(arena.x+95+col*74+sway,arena.y+55+row*52,16,"#ff72ba",true,"rect",30,30,"para/para0.png");if(((Math.floor(t)+row*7+col)%11)===0)push(arena.x+95+col*74+sway,arena.y+75+row*52+((t*165)%arena.h),8,"#ff6375",false,"rect",13,19,"damnit/mttsheart1.png");}if(Math.floor(t)%6<1)push(arena.x+((t*180)%arena.w),arena.y+arena.h-25,10,"#4ba9ff",false,"laser",90,10,"bot0/spr_lasermachine_b_0.png");}
  else if(attack===7){for(let ring=0;ring<6;ring++)for(let i=0;i<12;i++){const a=i*Math.PI/6+t*(.7+ring*.25)*(ring%2?1:-1),d=45+ring*42;push(arena.x+arena.w/2+Math.cos(a)*d,arena.y+arena.h/2+Math.sin(a)*d,8,"#7ddcff",false,"rect",13,22,"bolt.png");}for(let i=0;i<5;i++){const a=i*Math.PI*2/5+t*.9;push(arena.x+arena.w/2+Math.cos(a)*100,arena.y+arena.h/2+Math.sin(a)*100,18,"#ff6aa7",true,"rect",34,34,"para/para0.png");}}
  else if(attack===8){for(let col=0;col<11;col++){const beat=Math.floor(t*4);if((col+beat)%4!==0){const y=arena.y+((t*230+col*47)% (arena.h+80))-40;push(arena.x+35+col*57,y,9,"#77dcff",false,"rect",14,25,"bolt.png");}}for(let row=0;row<3;row++)for(let col=0;col<7;col++){const y=arena.y+arena.h+40-((t+row*.4)*130%(arena.h+80));push(arena.x+80+col*80,y,13,col%3===0?"#ffcf3c":"#ddd",col%3===0,"rect",24,24,col%3===0?"plus/plus0.png":"box.png");}}
  else if(attack===9){const direction=t<7.5?1:-1;for(let col=0;col<4;col++)for(let row=0;row<12;row++){const y=arena.y+arena.h-((t*180*direction+row*38+2000)% (arena.h+80));push(arena.x+arena.w/2-75+col*50,y,12,col===1||col===2?"#ddd":"#ffcf3c",true,"rect",23,23,col===1||col===2?"sbox/sbox.png":"plus/plus0.png");}laser("h",arena.y+70,1.8,11);laser("v",arena.x+arena.w-80,3.3,18);if(Math.floor(t*3)%5===0)push(arena.x+arena.w/2,arena.y+25,12,"#ff75ad",true,"rect",32,32,"para/para0.png");}
  else {[["h",arena.y+45,.2],["v",arena.x+105,.2],["h",arena.y+arena.h-45,1.5],["v",arena.x+arena.w-105,1.5],["h",arena.y+90,2.8],["v",arena.x+arena.w/2,3.3],["h",arena.y+arena.h/2,4.1],["v",arena.x+arena.w-70,5.4]].forEach(v=>laser(...v,15));for(let i=0;i<10;i++){const x=arena.x+arena.w+60-((t-3.3)*270+i*70);if(t>3.3)push(x,arena.y+arena.h-55,12,i%3?"#4ba9ff":"#ff8a38",false,"rect",24,17,i%3?"bot0/spr_lasermachine_b_0.png":"bot0/spr_lasermachine_o_0.png");}}
  return out;
}

function x125Hazards(attack, t, arena, player, locks, destroyed, destroyedAt) {
  if (attack === 10) return x125FinalHazards(t, player, locks, destroyed, destroyedAt);
  if (attack === 9) return x125TimeflowOneHazards(t, player, locks, destroyed, destroyedAt);
  if (attack === 8) return x125PianoOneHazards(t, player, locks, destroyed, destroyedAt);
  if (attack === 7) return x125CircleMadnessHazards(t, player, locks, destroyed);
  if (attack === 6) return x125SpaceInvadersHazards(t, player, locks, destroyed);
  if (attack === 5) return x125OrangeTrapsHazards(t);
  if (attack === 4) return x125YellowTwoHazards(t, player, locks, destroyed, destroyedAt);
  if (attack === 3) return x125YellowOneHazards(t, player, locks, destroyed, destroyedAt);
  return attack === 2 ? x125AttackTwoHazards(t, player, locks) : x125AttackOneHazards(t);
  const result = [];
  const add = (x, y, r = 10, color = "#fff", shootable = false, shape = "circle", w = 0, h = 0) =>
    result.push({ x, y, r, color, shootable, shape, w: w || r * 2, h: h || r * 2 });
  const n = Math.floor(t * 4);
  if (attack === 1) {
    for (let i = Math.max(0, n - 24); i <= n + 4; i += 1) add(arena.x + 25 + x125Hash(i, 1) * (arena.w - 50), arena.y + ((t * 145 + i * 73) % (arena.h + 80)) - 40, 9, "#ffef65", true);
  } else if (attack === 2) {
    for (let i = 0; i < 10; i += 1) add(arena.x + ((t * 180 + i * 93) % (arena.w + 100)) - 50, arena.y + 28 + i * 35, 11, i % 2 ? "#ff8a38" : "#62b8ff", i % 3 === 0);
  } else if (attack === 3) {
    for (let i = 0; i < 16; i += 1) { const a = i * Math.PI / 8 + t * 0.8; const d = 35 + ((t * 55 + i * 19) % 300); add(arena.x + arena.w / 2 + Math.cos(a) * d, arena.y + arena.h / 2 + Math.sin(a) * d, 9, "#ff5f77", true); }
  } else if (attack === 4) {
    for (let i = 0; i < 8; i += 1) { const y = arena.y + 18 + i * 48; const gap = arena.x + 80 + x125Hash(Math.floor(t * 0.75), i) * (arena.w - 160); add(arena.x + arena.w / 2, y, 5, "#f7f7f7", false, "wall", arena.w, 9); result[result.length - 1].gap = gap; result[result.length - 1].gapW = 85; }
  } else if (attack === 5) {
    for (let i = 0; i < 18; i += 1) { const a = i * 0.8 + t * 1.9; const d = (t * 80 + i * 31) % 350; add(arena.x + arena.w / 2 + Math.cos(a) * d, arena.y + arena.h / 2 + Math.sin(a) * d, 8, "#cf65ff", i % 2 === 0); }
  } else if (attack === 6) {
    for (let i = 0; i < 7; i += 1) add(arena.x + 45 + i * 92, arena.y + ((t * (90 + i * 7) + i * 61) % arena.h), 13, i % 2 ? "#ff8a38" : "#4ba9ff", false);
  } else if (attack === 7) {
    for (let i = 0; i < 11; i += 1) { const phase = (t + i * 0.58) % 4; const x = arena.x + 35 + x125Hash(i, 7) * (arena.w - 70); add(x, arena.y + phase * arena.h / 4, phase > 3.15 ? 28 : 12, phase > 3.15 ? "#ff334f" : "#ffe75c", true); }
  } else if (attack === 8) {
    for (let row = 0; row < 4; row += 1) for (let col = 0; col < 9; col += 1) add(arena.x + 45 + col * 68 + Math.sin(t * 1.5 + row) * 35, arena.y + 35 + row * 52, 13, "#73ff98", true, "rect", 25, 19);
    for (let i = 0; i < 8; i += 1) add(arena.x + 40 + i * 78, arena.y + ((t * 170 + i * 53) % arena.h), 7, "#ff6478");
  } else if (attack === 9) {
    for (let i = 0; i < 30; i += 1) { const a = t * 2.4 + i * 0.55; const d = 18 + i * 12; add(arena.x + arena.w / 2 + Math.cos(a) * d, arena.y + arena.h / 2 + Math.sin(a) * d, 7, i % 2 ? "#fff" : "#ffd84d", i % 4 === 0); }
  } else {
    for (let i = 0; i < 28; i += 1) { const side = i % 4; const p = (t * (130 + i % 5 * 12) + i * 47) % (arena.w + arena.h); let x; let y; if (side < 2) { x = arena.x + (p % arena.w); y = side ? arena.y : arena.y + arena.h; } else { x = side === 2 ? arena.x : arena.x + arena.w; y = arena.y + (p % arena.h); } const cx = arena.x + arena.w / 2; const cy = arena.y + arena.h / 2; const q = Math.min(1, (t % 2.2) / 2.2); add(x + (cx - x) * q, y + (cy - y) * q, 8, i % 3 ? "#ff4365" : "#61d8ff", i % 3 === 0); }
  }
  return result;
}

// Exact 640x480 coordinate translation of Lua/Waves/attack1.lua.
function x125AttackOneHazards(t) {
  const out = [];
  const toCanvasY = (luaY) => 480 - luaY;
  const blasters = [
    [-30,510,180,220,.2,270,0,.75,.55], [-30,510,260,290,.2,0,0,.76,.55],
    [670,-30,460,100,.2,90,0,.77,.55], [670,-30,380,30,.2,180,0,.78,.55],
    [670,510,320,290,1.5,0,0,.75,.55], [670,510,460,160,1.5,90,0,.76,.55],
    [-30,-30,320,30,1.5,180,0,.77,.55], [-30,-30,180,160,1.5,270,0,.78,.55],
    [-30,510,180,220,2.8,270,0,.75,.55], [-30,510,260,290,2.8,0,0,.76,.55],
    [670,-30,460,100,2.8,90,0,.77,.55], [670,-30,380,30,2.8,180,0,.78,.55],
    [-90,240,90,260,4.1,270,2,.8,.9], [730,240,550,60,5.4,90,2,.8,.9]
  ];
  for (const [sx,sy,ex,ey,start,rotation,size,delay,length] of blasters) {
    const age = t - start;
    if (age < 0 || age > 3) continue;
    const travel = .33333;
    const progress = age < travel ? Math.min(1, Math.pow(Math.max(0, age), .3) / Math.pow(travel, .3)) : 1;
    let lx = sx + (ex - sx) * progress;
    let ly = sy + (ey - sy) * progress;
    if (age >= delay) {
      const kick = Math.pow(age - delay, 4) * 1000;
      if (rotation === 0) ly = Math.min(680, ey + kick);
      if (rotation === 90) lx = Math.min(840, ex + kick);
      if (rotation === 180) ly = Math.max(-200, ey - kick);
      if (rotation === 270) lx = Math.max(-200, ex - kick);
    }
    const firing = age >= delay;
    const fireFrame = Math.min(5, Math.max(0, Math.floor((age - delay) * 30)));
    const dimensions=x125GasterSize(size);
    out.push({ x:lx, y:toCanvasY(ly), r:dimensions.headW/2, w:dimensions.headW, h:dimensions.headH,
      shape:"sprite", sprite:firing ? `gbfire/gb_${size}_0_${fireFrame}.png` : `gaster${size}/gb0.png`,
      // Canvas uses clockwise-positive rotation; the Lua engine used the opposite sign.
      rotation:rotation, dangerous:false });
    const beamLive = age >= delay + 4/30 && age < delay + length;
    const beamWarn = age >= delay && age < delay + length;
    if (!beamWarn) continue;
    if(x125GasterVisible(lx,ly))out.push(x125GasterBeam(`a1-beam-${start}-${ex}-${ey}`,lx,ly,rotation,size,beamLive,beamLive?"#fff":"rgba(255,255,255,.25)"));
  }
  const botGroups = [
    {start:3.4, xs:[700,850,1000,1150], colors:["orange","blue","orange","blue"]},
    {start:5.6, xs:[700,825,950,1075], colors:["orange","blue","blue","orange"]}
  ];
  for (const group of botGroups) {
    const age=t-group.start;
    if(age<0) continue;
    group.xs.forEach((startX,i)=>{
      const x=startX-age*350;
      if(x < -80 || x > 1220) return;
      const color=group.colors[i];
      const frame=Math.min(4,Math.max(0,Math.floor(age*12)%5));
      out.push(...x125LaserBotParts(`a1-bot-${group.start}-${i}`,x,400,0,color,frame));
    });
  }
  return out;
}

function x125AttackTwoHazards(t, player, locks) {
  const out=[];
  const toY=(y)=>480-y;
  const defs=[
    [670,510,420,340,.2,0,0,.75,.55],[670,510,320,340,.2,0,1,.77,.55],[670,510,220,340,.2,0,0,.79,.55],
    [-30,510,130,280,.7,270,0,.75,.55],[-30,510,130,182,.7,270,1,.77,.55],[-30,510,130,85,.7,270,0,.79,.55],
    [-30,-30,245,30,1.5,180,0,.75,.55],[-30,-30,395,30,1.5,180,0,.77,.55],
    [670,-30,510,128,2,90,0,.75,.55],[670,-30,510,240,2,90,0,.77,.55],
    [670,510,-42,340,3.6,0,1,.8,.55],[-30,510,130,-42,4.4,270,1,.8,.55],
    [-30,-30,-42,30,5.2,180,1,.8,.55],[670,-30,510,-42,6,90,1,.8,.55]
  ];
  defs.forEach((def,index)=>{
    let [sx,sy,ex,ey,start,rotation,size,delay,length]=def;
    const age=t-start;if(age<0||age>3)return;
    const lockKey=`a2:${index}`;
    if((ex===-42||ey===-42)&&!locks.has(lockKey)) locks.set(lockKey,{x:player.x,y:480-player.y});
    const lock=locks.get(lockKey);
    if(ex===-42)ex=lock?.x??320;if(ey===-42)ey=lock?.y??160;
    const travel=.33333,progress=age<travel?Math.min(1,Math.pow(Math.max(0,age),.3)/Math.pow(travel,.3)):1;
    let lx=sx+(ex-sx)*progress,ly=sy+(ey-sy)*progress;
    if(age>=delay){const kick=Math.pow(age-delay,4)*1000;if(rotation===0)ly=Math.min(680,ey+kick);if(rotation===90)lx=Math.min(840,ex+kick);if(rotation===180)ly=Math.max(-200,ey-kick);if(rotation===270)lx=Math.max(-200,ex-kick);}
    const firing=age>=delay,fireFrame=Math.min(5,Math.max(0,Math.floor((age-delay)*30))),dimensions=x125GasterSize(size);
    out.push({x:lx,y:toY(ly),r:dimensions.headW/2,w:dimensions.headW,h:dimensions.headH,shape:"sprite",sprite:firing?`gbfire/gb_${size}_0_${fireFrame}.png`:`gaster${size}/gb0.png`,rotation:rotation,dangerous:false});
    const beamLive=age>=delay+4/30&&age<delay+length,beamWarn=age>=delay&&age<delay+length;if(!beamWarn)return;
    if(x125GasterVisible(lx,ly))out.push(x125GasterBeam(`a2-beam-${index}`,lx,ly,rotation,size,beamLive,beamLive?"#fff":"rgba(255,255,255,.25)"));
  });
  const bots=[
    [700,300,2.8,-200,0,0],[-50,70,3.6,200,0,180],[480,600,4.4,0,-200,90],[160,-100,5.2,0,200,270]
  ];
  bots.forEach(([sx,sy,start,vx,vy,rotation])=>{
    const age=t-start;if(age<0)return;const x=sx+vx*age,luaY=sy+vy*age,y=toY(luaY);if(x<-80||x>720||y<-80||y>560)return;
    const frame=Math.min(4,Math.max(0,Math.floor(age*12)%5));out.push(...x125LaserBotParts(`a2-bot-${start}-${rotation}`,x,luaY,rotation,"blue",frame));
  });
  return out;
}

function x125YellowOneHazards(t, player, locks, destroyed, destroyedAt) {
  const out=[];
  const toY=(y)=>480-y;
  const onScreen=(x,y)=>x>-35&&x<675&&y>-35&&y<515;
  const pushMoving=(id,x,y,sprite,shootable=true,w=24,h=24,dangerous=true)=>{
    if(onScreen(x,y))out.push({id,x,y:toY(y),w,h,r:Math.min(w,h)/2,shape:"sprite",sprite,shootable,dangerous});
  };
  const pushBombExplosion=(id,x,canvasY,age,soundKey=id)=>{
    if(age<0||age>=.4)return;
    const frame=Math.min(6,Math.max(0,Math.floor(age*18)));
    out.push({id:`${id}-blast-h`,x:320,y:canvasY,w:640,h:22,r:11,shape:"laser",sprite:`plus/hor${frame}.png`,dangerous:true,color:"#fff"});
    out.push({id:`${id}-blast-v`,x,y:240,w:22,h:480,r:11,shape:"laser",sprite:`plus/ver${frame}.png`,dangerous:true,color:"#fff"});
    out.push({id:`${id}-blast-c`,x,y:canvasY,w:42,h:42,r:21,shape:"sprite",sprite:`plus/blast${frame}.png`,dangerous:true,soundEvent:`bomb:${soundKey}`});
  };
  // Three rows of seven shootable boxes, exactly 24 px apart and 0.16 s apart.
  for(let col=0;col<7;col++)for(let row=0;row<3;row++){
    const start=row*(24/150),age=t-start;if(age<0)continue;
    pushMoving(`y1-box-${col}-${row}`,248+col*24,540-150*age,"sbox/sbox.png",true,24,24,true);
  }
  // First bomb wall (can be accidentally shot).
  for(let col=0;col<7;col++){
    const age=t-2.2,id=`y1-bomb-fast-${col}`,x=248+col*24,y=540-150*age;if(age<0)continue;
    const hitAt=destroyedAt?.get(id);
    if(hitAt==null)pushMoving(id,x,y,"plus/plus0.png",true,24,30,true);
    else {const hitY=540-150*(hitAt-2.2);pushBombExplosion(id,x,toY(hitY),t-hitAt);}
  }
  const metts=[];
  [0,.4].forEach((offset,row)=>{
    metts.push({id:`left-${row}`,x:200,start:2.6+offset,fling:-1,ammo:2,first:1,delay:1});
    metts.push({id:`right-${row}`,x:440,start:2.6+offset,fling:1,ammo:2,first:1,delay:1});
  });
  [250,316,382].forEach((x,index)=>metts.push({id:`front-${index}`,x,start:3.8,fling:-1,ammo:10,first:1.2,delay:1,stop:260}));
  for(const mett of metts){
    const age=t-mett.start;if(age<0)continue;
    let sourceY;
    if(mett.stop){const moved=100*Math.min(age,1.2)+60*Math.max(0,age-1.2);sourceY=Math.max(mett.stop,540-moved);}
    else sourceY=540-(200*Math.min(age,1.2)+80*Math.max(0,age-1.2));
    let shotCount=0;
    const mettDestroyed=destroyed?.has(`y1-mett-${mett.id}`);
    for(let shot=0;shot<mett.ammo;shot++){
      if(mettDestroyed)break;
      const fireAt=mett.first+shot*mett.delay+.8;if(age<fireAt)continue;shotCount++;
      const absoluteFire=mett.start+fireAt,key=`y1-heart-${mett.id}-${shot}`;
      if(!locks.has(key))locks.set(key,{x:player.x,y:player.y,ox:mett.x+3,oy:toY(sourceY-10)});
      const target=locks.get(key),heartAge=t-absoluteFire;
      const originX=target.ox,originY=target.oy,angle=Math.atan2(target.y-originY,target.x-originX);
      const hx=originX+Math.cos(angle)*150*heartAge,hy=originY+Math.sin(angle)*150*heartAge;
      if(hx>-40&&hx<680&&hy>-40&&hy<520)out.push({id:key,x:hx,y:hy,w:24,h:24,r:9,shape:"sprite",sprite:"para/heart36.png",dangerous:true});
    }
    const shootingStart=mett.first+Math.min(shotCount,mett.ammo-1)*mett.delay;
    const animAge=age-shootingStart,frame=animAge>=0&&animAge<1.2?Math.min(17,Math.floor(animAge*15)):0;
    let mx=mett.x;if(shotCount>=mett.ammo){const doneAge=Math.max(0,age-(mett.first+(mett.ammo-1)*mett.delay+1.2));mx+=Math.pow(doneAge,3)*200*mett.fling;}
    if(!mettDestroyed)pushMoving(`y1-mett-${mett.id}`,mx,sourceY,"para/para0.png",true,46,58,false);
  }
  // Slow bomb row; it detonates after its 4.5 second fuse.
  for(let col=0;col<7;col++){
    const age=t-5.4;if(age<0)continue;const id=`y1-bomb-slow-${col}`,x=248+col*24,y=540-60*age,hitAt=destroyedAt?.get(id);
    const explodeAt=hitAt==null?9.9:hitAt;
    if(t<explodeAt)pushMoving(id,x,y,"plus/plus0.png",true,24,30,true);
    else {const explosionY=hitAt==null?toY(540-60*(9.9-5.4)):toY(540-60*(hitAt-5.4));pushBombExplosion(id,x,explosionY,t-explodeAt,hitAt==null?"final-row":id);}
  }
  // Final right-side Gaster Blaster.
  const age=t-9;
  if(age>=0&&age<=3){const sx=670,sy=-30,ex=510,ey=268,rotation=90,delay=.75,length=.55,travel=.33333,progress=age<travel?Math.min(1,Math.pow(age,.3)/Math.pow(travel,.3)):1;let lx=sx+(ex-sx)*progress,ly=sy+(ey-sy)*progress;if(age>=delay)lx=Math.min(840,ex+Math.pow(age-delay,4)*1000);const firing=age>=delay,frame=Math.min(5,Math.max(0,Math.floor((age-delay)*30))),dimensions=x125GasterSize(0);out.push({id:"y1-final-gb",x:lx,y:toY(ly),w:dimensions.headW,h:dimensions.headH,r:dimensions.headW/2,shape:"sprite",sprite:firing?`gbfire/gb_0_0_${frame}.png`:"gaster0/gb0.png",rotation,dangerous:false});if(age>=delay&&age<delay+length&&x125GasterVisible(lx,ly))out.push(x125GasterBeam("y1-final-beam",lx,ly,rotation,0,age>=delay+4/30,age>=delay+4/30?"#fff":"rgba(255,255,255,.25)"));}
  return out;
}

function x125YellowTwoHazards(t, player, locks, destroyed, destroyedAt) {
  const out=[],toY=(y)=>480-y;
  const sprite=(id,x,y,path,w,h,dangerous=true,shootable=false)=>{if(x>-60&&x<700&&y>-60&&y<540)out.push({id,x,y:toY(y),w,h,r:Math.min(w,h)/2,shape:"sprite",sprite:path,dangerous,shootable});};
  const movingY=(start,end,age)=>Math.max(end,start-(200*Math.min(age,1.5)+60*Math.max(0,age-1.5)));
  const heart=(key,fireAt,ox,oy)=>{if(t<fireAt)return;if(!locks.has(key))locks.set(key,{x:player.x,y:player.y,ox,oy:toY(oy)});const q=locks.get(key),age=t-fireAt,a=Math.atan2(q.y-q.oy,q.x-q.ox),x=q.ox+Math.cos(a)*150*age,y=q.oy+Math.sin(a)*150*age;if(x>-40&&x<680&&y>-40&&y<520)out.push({id:key,x,y,w:24,h:24,r:9,shape:"sprite",sprite:"para/heart36.png",dangerous:true});};
  // Opening rotating ring with the deliberate 60-degree opening.
  for(let deg=0,index=0;deg<=280;deg+=20,index++){const age=t;if(age>4)break;const a=(deg+160*age)*Math.PI/180,cx=320,cy=440-130*age;sprite(`y2-ring-${index}`,cx+Math.cos(a)*82,cy+Math.sin(a)*82,"bolt.png",18,30,true,false);}
  for(let col=0;col<7;col++){const y=545-130*t;sprite(`y2-top-box-${col}`,248+col*24,y,"sbox/sbox.png",24,24,true,true);}
  // Two expanding spinning bolt circles thrown diagonally from above.
  [[2,50,150],[2.8,590,-140]].forEach(([start,sx,vx],group)=>{const age=t-start;if(age<0||age>3)return;const cx=sx+vx*age,cy=540-250*age,r=10+age*16;for(let deg=0,index=0;deg<=320;deg+=40,index++){const a=(deg+360*age)*Math.PI/180;sprite(`y2-small-${group}-${index}`,cx+Math.cos(a)*r,cy+Math.sin(a)*r,"bolt.png",18,30,true,false);}});
  const shielded=[
    {id:"left",mx:256,cx:260,startY:752,endY:412,shieldStart:740,shieldEnd:400,spin:-90,first:1.5,delay:2},
    {id:"center",mx:316,cx:320,startY:652,endY:312,shieldStart:640,shieldEnd:300,spin:100,first:1.2,delay:1},
    {id:"right",mx:376,cx:380,startY:752,endY:412,shieldStart:740,shieldEnd:400,spin:-90,first:1.5,delay:2}
  ];
  for(const mett of shielded){const age=t-2.8;if(age<0)continue;const my=movingY(mett.startY,mett.endY,age),cy=movingY(mett.shieldStart,mett.shieldEnd,age),mettId=`y2-mett-${mett.id}`,dead=destroyed.has(mettId),deathAt=destroyedAt.get(mettId);let fired=0;if(!dead){for(let n=0;n<30;n++){const fireAt=2.8+mett.first+n*mett.delay+.8;if(fireAt>t)break;fired++;heart(`y2-heart-${mett.id}-${n}`,fireAt,mett.mx+3,my-10);}sprite(mettId,mett.mx,my,"para/para0.png",46,58,false,true);}
    const radius=deathAt==null?45:45+Math.max(0,t-deathAt)*300;
    for(let deg=0,index=0;deg<=320;deg+=40,index++){const boxId=`y2-shield-${mett.id}-${index}`;if(destroyed.has(boxId))continue;const a=(deg+mett.spin*age)*Math.PI/180;sprite(boxId,mett.cx+Math.cos(a)*radius,cy+Math.sin(a)*radius,"sbox/sbox.png",24,24,true,true);}
  }
  // Deterministic equivalents of the source's random interruptions every 4.2 seconds.
  const interruptions=["gaster","mett","bot","gaster","bot","mett"];
  interruptions.forEach((kind,index)=>{const start=6.5+index*4.2,age=t-start;if(age<0||age>5)return;
    if(kind==="mett")for(const [x,side] of [[160,-1],[480,1]]){const y=540-(220*Math.min(age,1)+80*Math.max(0,age-1)),base=`y2-extra-mett-${index}-${x}`;if(!destroyed.has(base)){sprite(base,x,y,"para/para0.png",46,58,false,true);heart(`${base}-heart-0`,start+1.6,x+3,y-10);heart(`${base}-heart-1`,start+2.6,x+3,y-10);}}
    if(kind==="bot")for(let n=0;n<2;n++){const fromRight=index%2===0,x=fromRight?670+n*110:-30-n*110,bx=x+(fromRight?-300:300)*age,color=(index+n)%2?"blue":"orange";out.push(...x125LaserBotParts(`y2-bot-${index}-${n}`,bx,70,180,color,Math.floor(age*12)%5));}
    if(kind==="gaster"){const targetKey=`y2-gaster-target-${index}`;if(!locks.has(targetKey))locks.set(targetKey,{x:player.x,y:480-player.y});const q=locks.get(targetKey);[[670,510,468,q.y,90],[-30,-30,q.x,50,180]].forEach(([sx,sy,ex,ey,rot],n)=>{const travel=.33333,p=age<travel?Math.pow(age,.3)/Math.pow(travel,.3):1;let lx=sx+(ex-sx)*Math.min(1,p),ly=sy+(ey-sy)*Math.min(1,p);if(age>=.9){const kick=Math.pow(age-.9,4)*1000;if(rot===90)lx=Math.min(840,ex+kick);else ly=Math.max(-200,ey-kick);}const fire=age>=.9,frame=Math.min(5,Math.max(0,Math.floor((age-.9)*30))),dimensions=x125GasterSize(1);out.push({id:`y2-gb-${index}-${n}`,x:lx,y:toY(ly),w:dimensions.headW,h:dimensions.headH,r:dimensions.headW/2,shape:"sprite",sprite:fire?`gbfire/gb_1_0_${frame}.png`:"gaster1/gb0.png",rotation:rot,dangerous:false});if(fire&&age<1.45&&x125GasterVisible(lx,ly))out.push(x125GasterBeam(`y2-gb-beam-${index}-${n}`,lx,ly,rot,1,age>=1.033,age>=1.033?"#fff":"rgba(255,255,255,.25)"));});}
  });
  return out;
}

function x125OrangeTrapsHazards(t) {
  const out=[],toY=(y)=>480-y;
  const blasters=[
    [670,510,320,290,.2,0,0,.9,2.1],[-30,-30,280,30,.82,180,0,.9,1.5],[670,-30,360,30,.82,180,0,.9,1.5],
    [-30,510,240,290,1.4,0,0,.9,.9],[670,510,400,290,1.4,0,0,.9,.9],
    [-30,-30,240,30,2,180,0,.9,1.2],[670,-30,400,30,2,180,0,.9,1.2],[-30,510,90,290,2,0,0,.9,1.2],[670,510,550,290,2,0,0,.9,1.2],
    [-30,510,160,290,4,0,0,.9,1.9],[670,510,480,290,4,0,0,.9,1.9],[-30,-30,200,30,4.6,180,0,.9,1.3],[670,-30,440,30,4.6,180,0,.9,1.3],
    [-30,510,250,290,5.2,0,0,.9,.55],[670,510,390,290,5.2,0,0,.9,.55],[-30,510,320,290,6,0,0,.9,2.1],[670,-30,320,30,6,180,0,.9,2.1],
    [-30,-30,280,30,6.6,180,0,.9,1.5],[670,-30,360,30,6.6,180,0,.9,1.5],[-30,510,240,290,7.2,0,0,.9,.9],[670,510,400,290,7.2,0,0,.9,.9],
    [-30,240,90,160,8.8,270,1,.9,.55],[670,240,550,160,8.8,90,1,.9,.55],
    [-30,240,90,100,9.7,270,0,.9,.55],[670,240,550,100,9.7,90,0,.9,.55],[-30,240,90,220,9.7,270,0,.9,.55],[670,240,550,220,9.7,90,0,.9,.55],
    [-30,240,90,160,10.6,270,1,.9,.55],[670,240,550,160,10.6,90,1,.9,.55]
  ];
  blasters.forEach(([sx,sy,ex,ey,start,rotation,size,delay,length],index)=>{const age=t-start;if(age<0||age>4)return;const travel=.33333,p=age<travel?Math.min(1,Math.pow(age,.3)/Math.pow(travel,.3)):1;let lx=sx+(ex-sx)*p,ly=sy+(ey-sy)*p;if(age>=delay){const kick=Math.pow(age-delay,4)*1000;if(rotation===0)ly=Math.min(680,ey+kick);if(rotation===90)lx=Math.min(840,ex+kick);if(rotation===180)ly=Math.max(-200,ey-kick);if(rotation===270)lx=Math.max(-200,ex-kick);}const firing=age>=delay,frame=Math.min(5,Math.max(0,Math.floor((age-delay)*30))),dimensions=x125GasterSize(size);out.push({id:`o5-gb-${index}`,x:lx,y:toY(ly),w:dimensions.headW,h:dimensions.headH,r:dimensions.headW/2,shape:"sprite",sprite:firing?`gbfire/gb_${size}_0_${frame}.png`:`gaster${size}/gb0.png`,rotation,dangerous:false});if(age<delay||age>=delay+length||!x125GasterVisible(lx,ly))return;out.push(x125GasterBeam(`o5-beam-${index}`,lx,ly,rotation,size,age>=delay+4/30,age>=delay+4/30?"#fff":"rgba(255,255,255,.25)"));});
  const addBot=(id,x,sourceY,color)=>out.push(...x125LaserBotParts(id,x,sourceY,0,color,Math.floor(t*12)%5));
  [215,230,245,260,275,365,380,395,410,425].forEach((x,index)=>addBot(`o5-orange-${index}`,x,270,"orange"));
  if(t>=8.5){addBot("o5-blue-left",200,320,"blue");addBot("o5-blue-right",440,320,"blue");}
  return out;
}

function x125SpaceInvadersHazards(t, player, locks, destroyed) {
  const out=[],toY=(y)=>480-y,total=21;
  const alive=[];for(let row=0;row<3;row++)for(let col=0;col<7;col++){const id=`s6-invader-${row}-${col}`;if(!destroyed.has(id))alive.push({id,row,col});}
  const aliveColumns=[...new Set(alive.map(v=>v.col))],leftMost=aliveColumns.length?Math.min(...aliveColumns):0,rightMost=aliveColumns.length?Math.max(...aliveColumns):6;
  const speed=Math.min(20,total/Math.max(1,alive.length));
  let formation=locks.get("s6-formation");
  if(!formation){formation={lastT:t,stepClock:0,offset:0,dir:1,bounces:0,finished:false};locks.set("s6-formation",formation);}
  const dt=Math.max(0,Math.min(.12,t-formation.lastT));formation.lastT=t;formation.stepClock+=dt*speed;
  const leftLimit=-leftMost*60,rightLimit=80+(6-rightMost)*60;
  while(formation.stepClock>=.25&&!formation.finished){formation.stepClock-=.25;formation.offset+=5*formation.dir;if(formation.offset<leftLimit){formation.offset=leftLimit;formation.dir=1;formation.bounces++;}else if(formation.offset>rightLimit){formation.offset=rightLimit;formation.dir=-1;formation.bounces++;}if(formation.bounces>=16)formation.finished=true;}
  for(const invader of alive){const spawn=invader.row/16+invader.col/120,age=t-spawn;if(age<0)continue;const x=100+invader.col*60+formation.offset,y=320+invader.row*45-formation.bounces*22.5;if(y<-30)formation.finished=true;if(x<-40||x>680||y<-40||y>520)continue;const firstShot=2+((invader.row*7+invader.col)*37%90)/10,interval=Math.max(4,12-speed*.35);let animFrame=0;for(let n=0;n<10;n++){const fireAt=spawn+firstShot+n*interval;if(fireAt>t)break;const key=`s6-shot-${invader.row}-${invader.col}-${n}`;if(!locks.has(key)){const aimed=(invader.row+invader.col+n)%2===0;locks.set(key,{aimed,x:player.x,y:player.y,ox:x+3,oy:toY(y-10)});}const q=locks.get(key),shotAge=t-fireAt;if(shotAge>=0&&shotAge<4){if(q.aimed){const a=Math.atan2(q.y-q.oy,q.x-q.ox),hx=q.ox+Math.cos(a)*150*shotAge,hy=q.oy+Math.sin(a)*150*shotAge;if(hx>-30&&hx<670&&hy>-30&&hy<510)out.push({id:key,x:hx,y:hy,w:20,h:20,r:6,shape:"sprite",sprite:"para/heart36.png",dangerous:true});}else{const by=toY(y-10-200*shotAge);if(by>-30&&by<510)out.push({id:key,x:x+3,y:by,w:15,h:19,r:6,shape:"sprite",sprite:"bolt.png",dangerous:true});}animFrame=Math.min(17,Math.floor(Math.max(0,shotAge)*15));}}
    out.push({id:invader.id,x,y:toY(y),w:58,h:48,r:16,shape:"sprite",sprite:"para/para0.png",shootable:true,dangerous:true});
  }
  for(let index=0,start=4;start<=90;start+=6,index++){const age=t-start;if(age<0)continue;const fromLeft=index%2===0,luaX=(fromLeft?-50:690)+(fromLeft?180:-180)*age;if(luaX<-80||luaX>720)continue;out.push(...x125LaserBotParts(`s6-ufo-${index}`,luaX,430,0,"blue",Math.floor(t*15)%5));}
  return out;
}

function x125CircleMadnessHazards(t, player, locks, destroyed) {
  const out=[],cx=320,cy=480-185;
  const sprite=(id,x,y,path,w,h,dangerous=true,shootable=false)=>{if(x>-70&&x<710&&y>-70&&y<550)out.push({id,x,y,w,h,r:Math.min(w,h)*.34,shape:"sprite",sprite:path,dangerous,shootable});};
  const mettRadius=Math.max(200,440-220*t);
  for(let index=0;index<8;index++){
    const id=`s7-mett-${index}`;if(destroyed.has(id))continue;
    const angle=(index*40+50*t)*Math.PI/180,x=cx+Math.cos(angle)*mettRadius,y=cy-Math.sin(angle)*mettRadius;
    const first=1+x125Hash(index,71)*10,delay=Math.max(1.2,7-destroyed.size*.3);let animFrame=0;
    for(let shot=0;shot<4;shot++){
      const fireAt=first+shot*delay;if(t<fireAt)break;const key=`s7-heart-${index}-${shot}`;
      if(!locks.has(key)){const a=Math.atan2(player.y-(y+10),player.x-(x+3));locks.set(key,{x:x+3,y:y+10,vx:Math.cos(a)*150,vy:Math.sin(a)*150});}
      const q=locks.get(key),age=t-fireAt,hx=q.x+q.vx*age,hy=q.y+q.vy*age;
      if(age>=0&&age<5&&hx>-30&&hx<670&&hy>-30&&hy<510)sprite(key,hx,hy,"para/heart36.png",20,20,true,false);
      if(age>=0&&age<1.2)animFrame=Math.min(17,Math.floor(age*15));
    }
    sprite(id,x,y,"para/para0.png",58,48,true,true);
  }
  const starts=[1.7,3.2,4.7,6.2,7.7,9.2,10.7,12.2],shrink=[180,200,200,210,210,220,220,230],counts=[29,29,30,30,30,30,31,31];
  starts.forEach((start,group)=>{
    const age=t-start;if(age<0)return;const radius=Math.max(0,640-shrink[group]*age);if(radius<=0)return;
    const minSpeed=[10,15,20,30,40,45,60,40][group],span=[60,100,120,90,120,140,120,80][group];
    const sign=x125Hash(group,72)<.5?-1:1,rotationSpeed=(minSpeed+x125Hash(group,73)*span)*sign,offset=x125Hash(group,74)*360;
    for(let index=0;index<counts[group];index++){const angle=(index*9+offset+rotationSpeed*age)*Math.PI/180;sprite(`s7-bolt-${group}-${index}`,cx+Math.cos(angle)*radius,cy-Math.sin(angle)*radius,"bolt.png",15,19,true,false);}
  });
  return out;
}

function x125FinalTime(realTime) {
  const segments=[
    [13,1,1,0],[5,1,-1,-2],[4.75,-1,1.25,2],[10,1.25,1,-.2],
    [9.6,1,1.5,.1],[10,1.5,.75,-.4],[13,.75,1,.25],[20,1,1/12,-.1]
  ];
  let remaining=Math.max(0,realTime),value=0;
  for(const [length,start,limit,rate] of segments){const d=Math.min(remaining,length);if(d<=0)break;const ramp=rate===0?0:Math.min(d,Math.abs((limit-start)/rate));value+=start*ramp+rate*ramp*ramp/2+(d-ramp)*limit;remaining-=d;}
  return value;
}

function x125FinalHazards(realTime, player, locks, destroyed, destroyedAt) {
  const out=[],toY=(y)=>480-y,t=x125FinalTime(realTime);
  const sprite=(id,x,luaY,path,w,h,dangerous=true,shootable=false)=>{const y=toY(luaY);if(x<=-80||x>=720||y<=-80||y>=560)return null;const item={id,x,y,w,h,r:Math.min(w,h)*.35,shape:"sprite",sprite:path,dangerous,shootable};out.push(item);return item;};
  const explosion=(id,x,luaY,age)=>{if(age<0||age>=.4)return;const frame=Math.min(6,Math.floor(age*18)),y=toY(luaY);out.push({id:`${id}-h`,x:320,y,w:640,h:20,r:10,shape:"laser",sprite:`plus/hor${frame}.png`,dangerous:true,soundEvent:`bomb:${id}`});out.push({id:`${id}-v`,x,y:240,w:20,h:480,r:10,shape:"laser",sprite:`plus/ver${frame}.png`,dangerous:true});out.push({id:`${id}-c`,x,y,w:20,h:20,r:10,shape:"sprite",sprite:`plus/blast${frame}.png`,dangerous:true});};
  if(t<14){[[260,330],[380,330]].forEach(([x,y],i)=>out.push(...x125LaserBotParts(`s10-grid-v-${i}`,x,y,0,"orange",Math.floor(realTime*15)%5)));[[180,135],[180,255]].forEach(([x,y],i)=>out.push(...x125LaserBotParts(`s10-grid-h-${i}`,x,y,270,"orange",Math.floor(realTime*15)%5)));for(let i=0;i<9;i++){const x=224+i*24,luaY=540-60*Math.max(0,t-.7);sprite(`s10-box-${i}`,x,luaY,"sbox/sbox.png",24,24,true,true);}}
  const addBlaster=(id,sx,sy,ex,ey,start,rotation,size=1,delay=.9)=>{const age=t-start;if(age<0||age>2.2)return;const travel=.33333,p=age<travel?Math.pow(Math.max(0,age),.3)/Math.pow(travel,.3):1;let x=sx+(ex-sx)*Math.min(1,p),y=sy+(ey-sy)*Math.min(1,p);if(age>=delay){const kick=Math.pow(age-delay,4)*1000;if(rotation===0)y=Math.min(680,ey+kick);else if(rotation===180)y=Math.max(-200,ey-kick);else if(rotation===90)x=Math.min(840,ex+kick);else x=Math.max(-200,ex-kick);}const firing=age>=delay,frame=Math.min(5,Math.max(0,Math.floor((age-delay)*30))),d=x125GasterSize(size);out.push({id,x,y:toY(y),w:d.headW,h:d.headH,r:d.headW/2,shape:"sprite",sprite:firing?`gbfire/gb_${size}_0_${frame}.png`:`gaster${size}/gb0.png`,rotation,dangerous:false});if(firing&&age<delay+.55&&x125GasterVisible(x,y))out.push(x125GasterBeam(`${id}-beam`,x,y,rotation,size,age>=delay+4/30,age>=delay+4/30?"#fff":"rgba(255,255,255,.25)"));};
  for(let n=0;n<10;n++){const start=.7+n*.7,row=(n*3+2)%5,col=(n*2+2)%5;addBlaster(`s10-opening-h-${n}`,-30,-30,156,115+row*40,start,270,n%3===0?0:1);addBlaster(`s10-opening-v-${n}`,-30,510,240+col*40,360,start,0,n%4===0?0:1);}
  for(let group=0;group<6;group++){const start=7+.8*group,age=t-start;if(age<0)continue;const centerY=680-Math.min(300,400*age),radius=Math.max(30,30+160*Math.max(0,age-.75)),speed=[50,-50,70,-70,100,-100][group];for(let i=0;i<10;i++){const a=(i*36+speed*age+group*31)*Math.PI/180;sprite(`s10-circle-${group}-${i}`,320+Math.cos(a)*radius,centerY+Math.sin(a)*radius,"bolt.png",15,19,true,false);}}
  for(let row=0;row<5;row++){const start=14+row*(24/78),age=t-start;if(age<0)continue;const bombCol=(row*3+1)%7;for(let col=0;col<7;col++){const id=`s10-wall-${row}-${col}`,x=248+col*24,luaY=500-78*age,hitAt=destroyedAt.get(id);if(col===bombCol){if(hitAt==null)sprite(id,x,luaY,"plus/plus0.png",24,30,true,true);else explosion(id,x,500-78*Math.max(0,x125FinalTime(hitAt)-start),realTime-hitAt);}else if(destroyedAt.get(`s10-wall-${row}-${bombCol}`)==null){const block=sprite(id,x,luaY,"box.png",24,24,true,false);if(block)block.blocksShot=true;}}}
  for(let row=0;row<11;row++){const start=18+row*1.74,age=t-start;if(age<0)continue;for(let col=0;col<7;col++){const id=`s10-fuse-${row}-${col}`,x=248+col*24,luaY=500-120*age,hitAt=destroyedAt.get(id),explodeAt=start+3.7;if(t<explodeAt&&hitAt==null)sprite(id,x,luaY,"plus/plus0.png",24,30,true,true);else{const when=hitAt==null?explodeAt:x125FinalTime(hitAt),boomY=500-120*(when-start);explosion(id,x,boomY,t-when);}}addBlaster(`s10-chase-${row}`,670,-30,510,50,start+2.8,90,0,.75);}
  if(t>=40){
    const base=41,
      patterns=["neutral","up","right","neutral","down","down","right","neutral"],
      offsets=[0,.33,.66,1,1.33,1.83,2.33,3];
    for(let cycle=0;cycle<4;cycle++)patterns.forEach((pattern,index)=>{
      const start=base+cycle*5.33333+offsets[index]-.25,age=t-start;
      const projectileSpeed=[200,400,600][Math.min(cycle,2)],maxAge=2*800/projectileSpeed;
      if(age<0||age>maxAge)return;

      // final.lua always launches all four pairs.  The hint moves one pair
      // to the centre; it does not remove an entire incoming direction.
      const topX=276,
        leftY=pattern==="up"?160:204,
        bottomX=pattern==="right"?320:364,
        rightY=pattern==="down"?160:116,
        lanes=[
          {x:topX-10,y:-210,vx:0,vy:projectileSpeed},
          {x:topX+10,y:-210,vx:0,vy:projectileSpeed},
          {x:-100,y:leftY-10,vx:projectileSpeed,vy:0},
          {x:-100,y:leftY+10,vx:projectileSpeed,vy:0},
          {x:bottomX-10,y:530,vx:0,vy:-projectileSpeed},
          {x:bottomX+10,y:530,vx:0,vy:-projectileSpeed},
          {x:740,y:rightY-10,vx:-projectileSpeed,vy:0},
          {x:740,y:rightY+10,vx:-projectileSpeed,vy:0}
        ];
      lanes.forEach((lane,laneIndex)=>{
        const x=lane.x+lane.vx*age,y=lane.y+lane.vy*age;
        sprite(`s10-rhythm-${cycle}-${index}-${laneIndex}`,x,480-y,"bolt.png",15,19,true,false);
      });
      if(age<.25)sprite(`s10-hint-${cycle}-${index}`,320,420,`hint${pattern}.png`,80,20,false,false);
    });
  }
  const phaseIcons=[[13,"rec"],[18,"rew"],[22.75,"ff"],[32.75,"play"],[42.35,"ff"],[52.35,"slow"],[65.35,"play"],[90,"play"]],icon=(phaseIcons.find(([end])=>realTime<end)||phaseIcons.at(-1))[1];out.push({id:"s10-flow",x:310,y:270,w:80,h:20,r:0,shape:"sprite",sprite:`timeflow/${icon}.png`,dangerous:false});
  return out;
}

function x125TimeflowOneHazards(realTime, player, locks, destroyed, destroyedAt) {
  const out=[],toY=(y)=>480-y;
  const warp=(value)=>{const u=Math.max(0,value-7.5);return value<=7.5?value:u<=4/3?7.5+u-.75*u*u:49/6-(u-4/3);},t=warp(realTime);
  const sprite=(id,x,luaY,path,w,h,dangerous=true,shootable=false)=>{const y=toY(luaY);if(x>-70&&x<710&&y>-70&&y<550)out.push({id,x,y,w,h,r:Math.min(w,h)*.36,shape:"sprite",sprite:path,dangerous,shootable});};
  const explode=(id,x,luaY,age)=>{if(age<0||age>=.4)return;const frame=Math.min(6,Math.floor(age*18)),y=toY(luaY);out.push({id:`${id}-h`,x:320,y,w:640,h:20,r:10,shape:"laser",sprite:`plus/hor${frame}.png`,dangerous:true,soundEvent:`bomb:${id}`});out.push({id:`${id}-v`,x,y:240,w:20,h:480,r:10,shape:"laser",sprite:`plus/ver${frame}.png`,dangerous:true});out.push({id:`${id}-c`,x,y,w:20,h:20,r:10,shape:"sprite",sprite:`plus/blast${frame}.png`,dangerous:true});};
  const shootableByRow=[[0,2],[1,3],[1],[2],[1]];
  [500,700,900,1100,1300].forEach((startY,row)=>{for(let col=0;col<4;col++){const id=`s9-grid-${row}-${col}`,x=282+26*col,luaY=startY-180*t,shootable=shootableByRow[row].includes(col),hitAt=destroyedAt.get(id);if(hitAt!=null){if(!shootable)explode(id,x,startY-180*warp(hitAt),realTime-hitAt);continue;}sprite(id,x,luaY,shootable?"sbox/sbox.png":"plus/plus0.png",24,shootable?24:30,true,true);}});
  const blasters=[[670,-30,440,105,1.8,90,1],[670,510,440,215,1.8,90,1],[-30,-30,200,160,3.3,270,0]];
  blasters.forEach(([sx,sy,ex,ey,start,rotation,size],index)=>{const age=t-start;if(age<0||age>4)return;const travel=.33333,p=age<travel?Math.pow(Math.max(0,age),.3)/Math.pow(travel,.3):1;let x=sx+(ex-sx)*Math.min(1,p),y=sy+(ey-sy)*Math.min(1,p);if(age>=.9){const kick=Math.pow(age-.9,4)*1000;if(rotation===90)x=Math.min(840,ex+kick);else x=Math.max(-200,ex-kick);}const firing=age>=.9,frame=Math.min(5,Math.max(0,Math.floor((age-.9)*30))),dimensions=x125GasterSize(size);out.push({id:`s9-gb-${index}`,x,y:toY(y),w:dimensions.headW,h:dimensions.headH,r:dimensions.headW/2,shape:"sprite",sprite:firing?`gbfire/gb_${size}_0_${frame}.png`:`gaster${size}/gb0.png`,rotation,dangerous:false});if(firing&&age<1.4&&x125GasterVisible(x,y))out.push(x125GasterBeam(`s9-beam-${index}`,x,y,rotation,size,age>=1.033,age>=1.033?"#fff":"rgba(255,255,255,.25)"));});
  const metts=[{x:280,start:4},{x:320,start:4},{x:360,start:4},{x:300,start:4.6},{x:340,start:4.6}];
  metts.forEach((mett,index)=>{const age=t-mett.start,id=`s9-mett-${index}`;if(age<0||destroyed.has(id))return;const luaY=mett.start===4?520-(140*Math.min(age,.8)+40*Math.max(0,age-.8)):540-(140*Math.min(age,.8)+40*Math.max(0,age-.8));for(let shot=0;shot<7;shot++){const fireAt=mett.start+1.4+shot;if(t<fireAt)break;const key=`s9-heart-${index}-${shot}`;if(!locks.has(key)){const originY=toY(luaY-10),a=Math.atan2(player.y-originY,player.x-(mett.x+3));locks.set(key,{x:mett.x+3,y:originY,vx:Math.cos(a)*150,vy:Math.sin(a)*150});}const q=locks.get(key),shotAge=t-fireAt;if(shotAge>=0&&shotAge<5)sprite(key,q.x+q.vx*shotAge,480-(q.y+q.vy*shotAge),"para/heart36.png",20,20,true,false);}sprite(id,mett.x,luaY,"para/para0.png",58,48,false,true);});
  out.push({id:"s9-flow-hud",x:310,y:270,w:80,h:20,r:0,shape:"sprite",sprite:realTime<7.5?"timeflow/rec.png":"timeflow/rew.png",dangerous:false});
  return out;
}

function x125PianoOneHazards(realTime, player, locks, destroyed, destroyedAt) {
  const out=[],toY=(y)=>480-y;
  const warp=(value)=>{const accelerated=Math.max(0,value-9);return value<=9?value:9+(accelerated<=1.25?accelerated+.1*accelerated*accelerated:1.40625+(accelerated-1.25)*1.25);},t=warp(realTime);
  const sprite=(id,x,luaY,path,w,h,dangerous=true,shootable=false)=>{const y=toY(luaY);if(x<=-70||x>=710||y<=-70||y>=550)return null;const item={id,x,y,w,h,r:Math.min(w,h)*.36,shape:"sprite",sprite:path,dangerous,shootable};out.push(item);return item;};
  const explode=(id,x,luaY,age)=>{if(age<0||age>=.4)return;const frame=Math.min(6,Math.floor(age*18)),y=toY(luaY);out.push({id:`${id}-h`,x:320,y,w:640,h:20,r:10,shape:"laser",sprite:`plus/hor${frame}.png`,dangerous:true,soundEvent:`bomb:${id}`});out.push({id:`${id}-v`,x,y:240,w:20,h:480,r:10,shape:"laser",sprite:`plus/ver${frame}.png`,dangerous:true});out.push({id:`${id}-c`,x,y,w:20,h:20,r:10,shape:"sprite",sprite:`plus/blast${frame}.png`,dangerous:true});};
  const addRows=(base)=>[0,.4,.8].forEach((offset,row)=>{const age=t-(base+offset);if(age<0)return;const bombCol=[1,5,3][row],bombId=`s8-${base}-${row}-${bombCol}`,hitAt=destroyedAt.get(bombId),hitTime=hitAt==null?null:warp(hitAt);for(let col=0;col<7;col++){const x=248+col*24,luaY=500-110*age,id=`s8-${base}-${row}-${col}`;if(col!==bombCol){if(hitTime==null){const block=sprite(id,x,luaY,"box.png",24,24,true,false);if(block)block.blocksShot=true;}}else if(hitTime==null)sprite(id,x,luaY,"plus/plus0.png",24,30,true,true);else explode(id,x,500-110*(hitTime-(base+offset)),t-hitTime);}});
  addRows(0);addRows(13);
  const signs=[0,1,2,3].map(i=>x125Hash(i,81)<.5?-1:1);
  const blasters=[[-30,510,184,160+signs[0]*22,2.8,270,.9],[-30,510,320+signs[1]*22,290,3.5,0,.9],[670,-30,456,160+signs[2]*22,4.8,90,.9],[670,-30,320+signs[3]*22,30,5.1,180,.9],[-30,510,184,160+signs[0]*22,15.8,270,.8],[-30,510,320+signs[1]*22,290,16.5,0,.8],[670,-30,456,160+signs[2]*22,17.8,90,.8],[670,-30,320+signs[3]*22,30,18.1,180,.8]];
  blasters.forEach(([sx,sy,ex,ey,start,rotation,delay],index)=>{const age=t-start;if(age<0||age>2)return;const travel=.33333,p=age<travel?Math.pow(age,.3)/Math.pow(travel,.3):1;let x=sx+(ex-sx)*Math.min(1,p),y=sy+(ey-sy)*Math.min(1,p);if(age>=delay){const kick=Math.pow(age-delay,4)*1000;if(rotation===0)y=Math.min(680,ey+kick);else if(rotation===180)y=Math.max(-200,ey-kick);else if(rotation===90)x=Math.min(840,ex+kick);else x=Math.max(-200,ex-kick);}const firing=age>=delay,frame=Math.min(5,Math.max(0,Math.floor((age-delay)*30))),size=x125GasterSize(0);out.push({id:`s8-gb-${index}`,x,y:toY(y),w:size.headW,h:size.headH,r:size.headW/2,shape:"sprite",sprite:firing?`gbfire/gb_0_0_${frame}.png`:"gaster0/gb0.png",rotation,dangerous:false});if(firing&&age<delay+.55&&x125GasterVisible(x,y))out.push(x125GasterBeam(`s8-beam-${index}`,x,y,rotation,0,age>=delay+4/30,age>=delay+4/30?"#fff":"rgba(255,255,255,.25)"));});
  const boltStarts=[];
  const buildMaze=(base,second=false)=>{const add=(x,offset)=>boltStarts.push([x,base+offset/180]);for(let i=0;i<=100;i+=20){add(346,i);add(386,i);}for(let i=1;i<=6;i++)add(346-i*15,100+i*3);for(let i=120;i<=200;i+=20)add(386,i);for(let i=1;i<=6;i++)add(386-i*15,200+i*3);for(let i=138;i<=218;i+=20)add(256,i);for(let i=238;i<=338;i+=20){add(256,i);add(296,i);}for(let i=1;i<=3;i++)add(296+i*15,338);for(let i=358;i<=438;i+=20)add(256,i);for(let i=1;i<=3;i++)add(256+i*15,438);for(let i=358;i<=438;i+=20)add(341,i);if(!second){for(let i=1;i<=3;i++)add(341+i*15,438);for(let i=458;i<=538;i+=20)add(301,i);for(let i=1;i<=3;i++)add(301+i*15,538);for(let i=458;i<=538;i+=20)add(386,i);}};
  buildMaze(6.2,false);buildMaze(6.2+558/180,true);
  boltStarts.forEach(([x,start],index)=>{const age=t-start;if(age>=0){const luaY=500-180*age;if(luaY>-30&&luaY<510)sprite(`s8-bolt-${index}`,x,luaY,"bolt.png",15,19,true,false);}});
  return out;
}

function startX125SoulBattle(initialState, resumeBackgroundOverride = null) {
  const overlay = document.createElement("div");
  overlay.className = "x125-battle-overlay";
  overlay.innerHTML = `<div class="x125-battle-main"><canvas width="640" height="480"></canvas></div><div class="x125-hp"><span>HP</span><div><i></i></div><b></b></div>`;
  document.body.appendChild(overlay);
  const canvas = overlay.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const owner = sameUserId(initialState.owner_id, currentUserId());
  const initialDestroyed=Array.isArray(initialState.destroyed)?initialState.destroyed.map(String):[],initialDestroyedAt=initialState.destroyed_at&&typeof initialState.destroyed_at==="object"?Object.entries(initialState.destroyed_at).map(([id,at])=>[String(id),Number(at)||0]):[];
  const runtime = { overlay, canvas, ctx, owner, serverState: initialState, x: Number(initialState.x ?? 0.5), y: Number(initialState.y ?? 0.5), targetX:Number(initialState.x ?? 0.5), targetY:Number(initialState.y ?? 0.5), observerStateAt:Number(initialState.updated_at || 0), syncBusy:false, observerSyncBusy:false, facing: initialState.facing || "up", hp: Number(initialState.hp || 0), maxHp: Number(initialState.max_hp || 100), keys: new Set(), isMoving:false, shots: Array.isArray(initialState.shots)?initialState.shots.map(s=>({...s})):[], destroyed: new Set(initialDestroyed), destroyedAt:new Map(initialDestroyedAt), deathFades:new Map(), playedSoundEvents:new Set(), transientAudio:new Set(), targetLocks:new Map(), lastAttack:0, lastSoundPhase:-1, lastShotAt:0, attack4ClearAt:0, attack6ClearAt:0, advancing:false, invulnerableUntil: 0, lastFrame: performance.now(), lastSync: 0, lastObserverSync:0, ended: false };
  x125BattleRuntime = runtime;
  const resumeBackgroundAfterBattle = resumeBackgroundOverride==null?Boolean(gameMusic && !gameMusic.paused && backgroundMusicEnabled):Boolean(resumeBackgroundOverride);
  x125AudioLock = true;
  if (gameMusic) gameMusic.pause();
  soundPlayers.burningEyes.loop = true;
  soundPlayers.burningEyes.muted = !backgroundMusicEnabled;
  soundPlayers.burningEyes.currentTime = 0;
  soundPlayers.burningEyes.play().catch(() => {});
  if (owner) apiPost("/api/game/train-pause", { user_id: currentUserId(), paused: true }).catch(() => {});
  const down = (e) => { if (!owner) return; const key = e.key.toLowerCase(); const shoot = e.code === "KeyZ" || key === "z" || key === "я"; if (["arrowup", "arrowdown", "arrowleft", "arrowright", "w", "a", "s", "d", "ц", "ф", "ы", "в"].includes(key) || shoot) e.preventDefault(); if (!shoot) runtime.keys.add(key); const yellowWave=[3,4,6,7,8,9,10].includes(runtime.lastAttack);if (shoot && !e.repeat && (!yellowWave||performance.now()-runtime.lastShotAt>=500)) { runtime.lastShotAt=performance.now();const dir = yellowWave?"up":runtime.facing; const shotSpeed=runtime.lastAttack===10?650:520; const velocity = { up:[0,-shotSpeed], down:[0,shotSpeed], left:[-shotSpeed,0], right:[shotSpeed,0] }[dir]; runtime.shots.push({ x:runtime.x, y:runtime.y, vx:velocity[0], vy:velocity[1] });const audio=soundPlayers.pew.cloneNode();audio.volume=soundPlayers.pew.volume;audio.play().catch(()=>{}); } };
  const up = (e) => runtime.keys.delete(e.key.toLowerCase());
  window.addEventListener("keydown", down); window.addEventListener("keyup", up);
  let arena = { x:242.5, y:255, w:155, h:130 };
  overlay.querySelectorAll("[data-attack]").forEach((button)=>button.addEventListener("click", async () => {
    if (!owner) return;
    const selected=Number(button.dataset.attack||1);const payload = await apiPost("/api/game/x125-battle-update", { user_id:currentUserId(), state:{restart_attack:selected} });
    runtime.serverState=payload.battle||runtime.serverState; runtime.x=.5; runtime.y=selected===2?(295-230)/180:.5; runtime.shots=[]; runtime.destroyed.clear();runtime.destroyedAt.clear();runtime.playedSoundEvents.clear();runtime.targetLocks.clear();runtime.attack4ClearAt=0;runtime.attack6ClearAt=0;runtime.advancing=false;runtime.lastAttack=0;runtime.lastSoundPhase=-1;
  }));
  const stopTransientBattleSounds = () => { runtime.transientAudio.forEach(audio=>{audio.pause();audio.currentTime=0;});runtime.transientAudio.clear(); };
  const finish = async (status = "completed") => {
    if(runtime.ended)return;
    runtime.ended=true;
    window.removeEventListener("keydown",down);
    window.removeEventListener("keyup",up);
    stopTransientBattleSounds();
    soundPlayers.burningEyes.pause();
    soundPlayers.burningEyes.currentTime=0;
    let finalBattle=runtime.serverState||initialState;
    if(owner&&status==="completed"){
      try{
        const payload=await apiPost("/api/game/x125-battle-update",{user_id:currentUserId(),state:{completed:true,complete_early:runtime.lastAttack===10,attack:10,x:runtime.x,y:runtime.y,facing:runtime.facing,shots:[]}});
        finalBattle=payload.battle||finalBattle;
      }catch(_){}
    }
    if(owner)apiPost("/api/game/train-pause",{user_id:currentUserId(),paused:false}).catch(()=>{});
    overlay.remove();
    if(status==="completed"){
      const eventId=Number(finalBattle?.id||initialState?.id||0);
      if(eventId)window.localStorage.setItem(`x125-battle-finished:${eventId}`,"yes");
      await playX125EramOutro(finalBattle?.reward_cp||0);
    }
    x125AudioLock=false;
    if(resumeBackgroundAfterBattle&&gameMusic&&backgroundMusicEnabled)gameMusic.play().catch(()=>{});
    if(x125BattleRuntime===runtime)x125BattleRuntime=null;
  };
  const frame = async (now) => {
    if (runtime.ended) return;
    const dt = Math.min(0.035, (now - runtime.lastFrame) / 1000); runtime.lastFrame = now;
    const state = runtime.serverState || initialState;
    if (state.status !== "active") { finish(state.status); return; }
    runtime.hp = Number(state.hp ?? runtime.hp); runtime.maxHp = Number(state.max_hp || runtime.maxHp);
    const elapsed = Math.max(0, Date.now() / 1000 - Number(state.started_at || 0));
    const wave = x125Timeline(elapsed); const attack=wave.attack, phase=wave.time, active=wave.active;
    if (elapsed >= X125_BATTLE_LENGTH) { finish("completed"); return; }
    const finalTime=attack===10?x125FinalTime(phase):0;
    arena=attack===2?{x:197.5,y:230,w:245,h:180}:(attack===3||attack===4)?{x:236,y:255,w:168,h:130}:attack===5?{x:145,y:255,w:350,h:130}:attack===6?{x:70,y:312,w:500,h:16}:attack===7?{x:212.5,y:230,w:215,h:180}:attack===8?{x:255,y:255,w:130,h:130}:attack===9?{x:267.5,y:255,w:105,h:130}:attack===10?(finalTime>=40?{x:255,y:255,w:130,h:130}:finalTime>=14?{x:236,y:220,w:168,h:200}:{x:220,y:220,w:200,h:200}):{x:242.5,y:255,w:155,h:130};
    if(owner&&attack===10&&finalTime>=62.5){finish("completed");return;}
    if(runtime.lastAttack!==attack){stopTransientBattleSounds();runtime.lastAttack=attack;runtime.lastSoundPhase=-1;runtime.targetLocks.clear();runtime.destroyed.clear();runtime.destroyedAt.clear();runtime.deathFades.clear();runtime.playedSoundEvents.clear();runtime.attack4ClearAt=0;runtime.attack6ClearAt=0;if(owner&&attack===2){runtime.x=.5;runtime.y=(295-230)/180;}else if(owner&&(attack===3||attack===4||attack===6||attack===8||attack===9)){runtime.x=.5;runtime.y=.5;}else if(owner&&attack===7){runtime.x=.5;runtime.y=(295-230)/180;}else if(owner&&attack===10){runtime.x=.5;runtime.y=.325;}}
    const soundSchedules={
      1:{intro:[.2,1.5,2.8,4.1,5.4],fire:[.95,2.25,3.55,4.9,6.2]},
      2:{intro:[.2,.7,1.5,2,3.6,4.4,5.2,6],fire:[.95,1.45,2.25,2.75,4.4,5.2,6,6.8]},
      3:{intro:[9],fire:[9.75]},
      4:{intro:[6.5,19.1],fire:[7.4,20]},
      5:{intro:[.2,.82,1.4,2,4,4.6,5.2,6,6.6,7.2,8.8,9.7,10.6],fire:[1.1,1.72,2.3,2.9,4.9,5.5,6.1,6.9,7.5,8.1,9.7,10.6,11.5]},
      8:{intro:[2.8,3.5,4.8,5.1,14.57,15.13,16.17,16.41],fire:[3.7,4.4,5.7,6,15.21,15.77,16.81,17.05]},
      9:{intro:[1.8,1.8,3.3],fire:[2.7,2.7,4.2]}
    },soundTimes=soundSchedules[attack]||{intro:[],fire:[]};
    const playBattleSound=(source)=>{const audio=source.cloneNode();audio.volume=source.volume;runtime.transientAudio.add(audio);audio.addEventListener("ended",()=>runtime.transientAudio.delete(audio),{once:true});audio.play().catch(()=>runtime.transientAudio.delete(audio));};
    if(active){const soundPhase=attack===9?(()=>{const u=Math.max(0,phase-7.5);return phase<=7.5?phase:u<=4/3?7.5+u-.75*u*u:49/6-(u-4/3);})():phase,rewinding=attack===9&&runtime.lastSoundPhase>=0&&soundPhase<runtime.lastSoundPhase;soundTimes.intro.forEach(at=>{if((!rewinding&&runtime.lastSoundPhase<at&&soundPhase>=at)||(rewinding&&runtime.lastSoundPhase>at&&soundPhase<=at))playBattleSound(soundPlayers.gasterIntro);});soundTimes.fire.forEach(at=>{if((!rewinding&&runtime.lastSoundPhase<at&&soundPhase>=at)||(rewinding&&runtime.lastSoundPhase>at&&soundPhase<=at))playBattleSound(soundPlayers.gasterFire);});runtime.lastSoundPhase=soundPhase;}
    if (owner) {
      const previousX=runtime.x,previousY=runtime.y;let dx=0,dy=0; if(runtime.keys.has("arrowleft")||runtime.keys.has("a")||runtime.keys.has("ф")){dx--;runtime.facing="left";} if(runtime.keys.has("arrowright")||runtime.keys.has("d")||runtime.keys.has("в")){dx++;runtime.facing="right";} if(runtime.keys.has("arrowup")||runtime.keys.has("w")||runtime.keys.has("ц")){dy--;runtime.facing="up";} if(runtime.keys.has("arrowdown")||runtime.keys.has("s")||runtime.keys.has("ы")){dy++;runtime.facing="down";} const minX=8/arena.w,maxX=1-minX,minY=8/arena.h,maxY=1-minY;if(attack===8||(attack===10&&finalTime>=40)){const gridLimit=44/130,gridMin=.5-gridLimit,gridMax=.5+gridLimit,step=440/130*dt;runtime.x=dx<0?Math.max(gridMin,runtime.x-step):dx>0?Math.min(gridMax,runtime.x+step):runtime.x>.5?Math.max(.5,runtime.x-step):Math.min(.5,runtime.x+step);runtime.y=dy<0?Math.max(gridMin,runtime.y-step):dy>0?Math.min(gridMax,runtime.y+step):runtime.y>.5?Math.max(.5,runtime.y-step):Math.min(.5,runtime.y+step);}else{const len=Math.hypot(dx,dy)||1;runtime.x=Math.max(minX,Math.min(maxX,runtime.x+dx/len*(150/arena.w)*dt));runtime.y=Math.max(minY,Math.min(maxY,runtime.y+dy/len*(150/arena.h)*dt));}runtime.isMoving=Math.hypot((runtime.x-previousX)*arena.w,(runtime.y-previousY)*arena.h)>.05;
      runtime.shots.forEach(s=>{s.x+=s.vx/arena.w*dt;s.y+=s.vy/arena.h*dt;}); runtime.shots=runtime.shots.filter(s=>{const sx=arena.x+s.x*arena.w,sy=arena.y+s.y*arena.h;return sx>-30&&sx<670&&sy>-60&&sy<540;});
    } else {
      const stateAt=Number(state.updated_at||0);
      if(stateAt!==runtime.observerStateAt){
        runtime.observerStateAt=stateAt;
        runtime.targetX=Number(state.x??.5);
        runtime.targetY=Number(state.y??.5);
        runtime.facing=state.facing||"up";
        runtime.shots=Array.isArray(state.shots)?state.shots.map(s=>({...s})):[];
        if(Number(state.destroyed_attack||attack)===attack){
          runtime.destroyed=new Set(Array.isArray(state.destroyed)?state.destroyed.map(String):[]);
          runtime.destroyedAt=new Map(state.destroyed_at&&typeof state.destroyed_at==="object"?Object.entries(state.destroyed_at).map(([id,at])=>[String(id),Number(at)||0]):[]);
        }
      }
      const follow=Math.min(1,dt*35);
      runtime.x+=(runtime.targetX-runtime.x)*follow;
      runtime.y+=(runtime.targetY-runtime.y)*follow;
      runtime.shots.forEach(s=>{s.x+=s.vx/arena.w*dt;s.y+=s.vy/arena.h*dt;});
      runtime.shots=runtime.shots.filter(s=>{const sx=arena.x+s.x*arena.w,sy=arena.y+s.y*arena.h;return sx>-30&&sx<670&&sy>-60&&sy<540;});
    }
    const px=arena.x+runtime.x*arena.w, py=arena.y+runtime.y*arena.h; let hazards=active?x125Hazards(attack,phase,arena,{x:px,y:py},runtime.targetLocks,runtime.destroyed,runtime.destroyedAt):[];
    hazards.forEach(h=>{if(h.soundEvent&&!runtime.playedSoundEvents.has(h.soundEvent)){runtime.playedSoundEvents.add(h.soundEvent);const audio=soundPlayers.plusExplode.cloneNode();audio.volume=soundPlayers.plusExplode.volume;audio.play().catch(()=>{});}});
    hazards.forEach((h,index)=>h.id=h.id||`${attack}:${index}`);
    if(owner&&runtime.shots.length){for(const shot of runtime.shots){const sx=arena.x+shot.x*arena.w,sy=arena.y+shot.y*arena.h,collisions=hazards.filter(h=>{if(runtime.destroyed.has(h.id))return false;if(h.blocksShot)return Math.abs(sx-h.x)<h.w/2+3&&Math.abs(sy-h.y)<h.h/2+8;return Math.hypot(sx-h.x,sy-h.y)<h.r+9;});if(collisions.some(h=>h.blocksShot)){shot.dead=true;continue;}const h=collisions.find(item=>item.shootable);if(h){runtime.destroyed.add(h.id);runtime.destroyedAt.set(h.id,phase);if(h.sprite==="para/para0.png")runtime.deathFades.set(h.id,{...h,startedAt:now});shot.dead=true;}}runtime.shots=runtime.shots.filter(s=>!s.dead);}
    hazards=hazards.filter(h=>!runtime.destroyed.has(h.id));
    if(owner&&attack===4&&["left","center","right"].every(id=>runtime.destroyed.has(`y2-mett-${id}`))){if(!runtime.attack4ClearAt)runtime.attack4ClearAt=now;if(now-runtime.attack4ClearAt>=1000&&!runtime.advancing){runtime.advancing=true;apiPost("/api/game/x125-battle-update",{user_id:currentUserId(),state:{restart_attack:5}}).then(p=>{runtime.serverState=p.battle||runtime.serverState;runtime.x=.5;runtime.y=.5;runtime.shots=[];runtime.destroyed.clear();runtime.destroyedAt.clear();runtime.playedSoundEvents.clear();runtime.targetLocks.clear();runtime.attack4ClearAt=0;runtime.lastAttack=0;runtime.lastSoundPhase=-1;}).catch(()=>{}).finally(()=>{runtime.advancing=false;});requestAnimationFrame(frame);return;}}
    const attack6Formation=runtime.targetLocks.get("s6-formation");
    if(owner&&attack===6&&(Array.from({length:21},(_,i)=>`s6-invader-${Math.floor(i/7)}-${i%7}`).every(id=>runtime.destroyed.has(id))||attack6Formation?.finished)){if(!runtime.attack6ClearAt)runtime.attack6ClearAt=now;if(now-runtime.attack6ClearAt>=1000&&!runtime.advancing){runtime.advancing=true;apiPost("/api/game/x125-battle-update",{user_id:currentUserId(),state:{restart_attack:7}}).then(p=>{runtime.serverState=p.battle||runtime.serverState;runtime.x=.5;runtime.y=(295-230)/180;runtime.shots=[];runtime.destroyed.clear();runtime.destroyedAt.clear();runtime.playedSoundEvents.clear();runtime.targetLocks.clear();runtime.attack6ClearAt=0;runtime.lastAttack=0;runtime.lastSoundPhase=-1;}).catch(()=>{}).finally(()=>{runtime.advancing=false;});requestAnimationFrame(frame);return;}}
    if(owner&&active&&now>runtime.invulnerableUntil){ const moving=runtime.isMoving,playerRadius=8; const hit=hazards.some(h=>{ if(h.dangerous===false)return false;if(h.shape==="wall"){if(h.gap&&Math.abs(px-h.gap)<h.gapW/2)return false;return Math.abs(py-h.y)<11;} const hx=h.hitX??h.x,hy=h.hitY??h.y,hw=h.hitW??h.w,hh=h.hitH??h.h;const collide=(h.shape==="rect"||h.shape==="laser")?Math.abs(px-hx)<hw/2+playerRadius&&Math.abs(py-hy)<hh/2+playerRadius:Math.hypot(px-h.x,py-h.y)<h.r+playerRadius; if(h.color==="#4ba9ff")return collide&&moving;if(h.color==="#ff8a38")return collide&&!moving;return collide;}); if(hit){runtime.invulnerableUntil=now+950;runtime.hp=runtime.hp<=1?0:Math.max(1,runtime.hp-7);const hitAudio=soundPlayers.battleHit.cloneNode();hitAudio.volume=soundPlayers.battleHit.volume;hitAudio.play().catch(()=>{});apiPost("/api/game/x125-battle-hit",{user_id:currentUserId()}).then(p=>{runtime.serverState=p.battle||runtime.serverState;if(p.game_state)applyGameState(p.game_state,{forceRefresh:true});}).catch(()=>{});} }
    ctx.fillStyle="#000";ctx.fillRect(0,0,640,480);if(attack===8||(attack===10&&finalTime>=40)){const piano=x125Image("pianomode.png");if(piano.complete&&piano.naturalWidth)ctx.drawImage(piano,arena.x,arena.y,arena.w,arena.h);}ctx.strokeStyle="#fff";ctx.lineWidth=5;ctx.strokeRect(arena.x,arena.y,arena.w,arena.h);
    hazards.forEach(h=>{ctx.fillStyle=h.color||"#fff";if(h.shape==="wall"){ctx.fillRect(h.x-h.w/2,h.y-h.h/2,Math.max(0,(h.gap-h.gapW/2)-(h.x-h.w/2)),h.h);ctx.fillRect(h.gap+h.gapW/2,h.y-h.h/2,(h.x+h.w/2)-(h.gap+h.gapW/2),h.h);}else if(h.shape==="laser"){const img=h.sprite?x125Image(h.sprite):null;if(img&&img.complete&&img.naturalWidth){ctx.globalAlpha=h.dangerous===false?.35:1;ctx.drawImage(img,h.x-h.w/2,h.y-h.h/2,h.w,h.h);ctx.globalAlpha=1;}else ctx.fillRect((h.hitX??h.x)-(h.hitW??h.w)/2,(h.hitY??h.y)-(h.hitH??h.h)/2,h.hitW??h.w,h.hitH??h.h);}else if(h.sprite){const img=x125Image(h.sprite);if(img.complete&&img.naturalWidth){const drawW=h.sprite==="para/para0.png"?img.naturalWidth:h.w,drawH=h.sprite==="para/para0.png"?img.naturalHeight:h.h;ctx.save();ctx.translate(h.x,h.y);ctx.rotate((h.rotation||0)*Math.PI/180);ctx.drawImage(img,-drawW/2,-drawH/2,drawW,drawH);ctx.restore();}else ctx.fillRect(h.x-h.w/2,h.y-h.h/2,h.w,h.h);}else if(h.shape==="rect")ctx.fillRect(h.x-h.w/2,h.y-h.h/2,h.w,h.h);else{ctx.beginPath();ctx.arc(h.x,h.y,h.r,0,Math.PI*2);ctx.fill();}});
    runtime.deathFades.forEach((ghost,id)=>{const progress=(now-ghost.startedAt)/650;if(progress>=1){runtime.deathFades.delete(id);return;}const img=x125Image("para/para0.png");if(img.complete&&img.naturalWidth){ctx.save();ctx.globalAlpha=Math.max(0,1-progress);ctx.translate(ghost.x,ghost.y);ctx.rotate((ghost.rotation||0)*Math.PI/180);ctx.drawImage(img,-img.naturalWidth/2,-img.naturalHeight/2,img.naturalWidth,img.naturalHeight);ctx.restore();}});
    ctx.fillStyle="#ffe735";runtime.shots.forEach(s=>ctx.fillRect(arena.x+s.x*arena.w-3,arena.y+s.y*arena.h-8,6,16));
    const redFinal=attack===10&&finalTime>=40,
      fixedUp=[3,4,6,7,8,9,10].includes(attack),
      soulFacing=fixedUp?"up":runtime.facing,
      // The transparent yellow-heart sprite points down in its source PNG,
      // so its directional angles are the reverse of the previous yh0 asset.
      soulAngle=redFinal?0:({up:Math.PI,right:-Math.PI/2,down:0,left:Math.PI/2}[soulFacing]??Math.PI);
    ctx.save();ctx.translate(px,py);ctx.rotate(soulAngle);ctx.globalAlpha=now<runtime.invulnerableUntil&&Math.floor(now/80)%2?.25:1;const soul=x125Image(redFinal?"rh0.png":"heartyellow0.png");if(soul.complete&&soul.naturalWidth)ctx.drawImage(soul,-8,-8,16,16);else{ctx.fillStyle=redFinal?"#ff3131":"#ffe735";ctx.fillRect(-8,-8,16,16);}ctx.restore();
    overlay.querySelector(".x125-hp b").textContent=`${runtime.hp} / ${runtime.maxHp}`;overlay.querySelector(".x125-hp i").style.width=`${Math.max(0,Math.min(100,runtime.hp/runtime.maxHp*100))}%`;
    if(owner&&now-runtime.lastSync>120&&!runtime.syncBusy){
      runtime.lastSync=now;
      runtime.syncBusy=true;
      apiPost("/api/game/x125-battle-update",{user_id:currentUserId(),state:{x:runtime.x,y:runtime.y,facing:runtime.facing,attack,shots:runtime.shots,destroyed:[...runtime.destroyed],destroyed_at:Object.fromEntries(runtime.destroyedAt)}}).then(p=>runtime.serverState=p.battle||runtime.serverState).catch(()=>{}).finally(()=>{runtime.syncBusy=false;});
    }
    if(!owner&&now-runtime.lastObserverSync>120&&!runtime.observerSyncBusy){
      runtime.lastObserverSync=now;
      runtime.observerSyncBusy=true;
      api(`/api/game/x125-battle?user_id=${currentUserId()}`).then(p=>{
        if(p?.battle&&Number(p.battle.id||0)===Number(initialState.id||0))runtime.serverState=p.battle;
      }).catch(()=>{}).finally(()=>{runtime.observerSyncBusy=false;});
    }
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}

async function handleKlipotaEvent(event = null) {
  const eventId = Number(event?.id || 0);
  if (!eventId || !sameUserId(event?.user_id, currentUserId())) return;
  const storageKey = `klipota-event:${currentUserId()}:${eventId}`;
  if (window.localStorage.getItem(storageKey) === "shown") return;
  window.localStorage.setItem(storageKey, "shown");

  const overlay = ensureFullscreenEventOverlay();
  const image = overlay.querySelector(".fullscreen-event-image");
  const card = overlay.querySelector(".fullscreen-event-message");
  card.classList.add("hidden");
  image.src = "/photo/special/rabbittriggered.png";
  image.alt = "Протокол кроликов";
  image.classList.remove("hidden");
  overlay.classList.remove("hidden");

  const audio = soundPlayers.overloadAlert;
  await new Promise((resolve) => {
    let finished = false;
    const done = () => {
      if (finished) return;
      finished = true;
      audio.removeEventListener("ended", done);
      resolve();
    };
    audio.addEventListener("ended", done, { once: true });
    try {
      audio.currentTime = 0;
      const playback = audio.play();
      if (playback?.catch) playback.catch(() => window.setTimeout(done, 1600));
    } catch (_) {
      window.setTimeout(done, 1600);
    }
    window.setTimeout(done, 12000);
  });
  image.classList.add("hidden");
  overlay.classList.add("hidden");
  await showFullscreenEventMessage("Перегрев клипота", event.text || "Для устранения перегрева клипота была привлечена команда кроликов.");
}

let voyagerWarningShowing=false;
async function handleVoyagerWarning(warning=null){
  const eventId=Number(warning?.id||0);
  if(!eventId||voyagerWarningShowing)return;
  const storageKey=`voyager-warning:${currentUserId()}:${lastActiveGameStartedAt||"game"}:${warning?.day||0}:${eventId}`;
  if(window.localStorage.getItem(storageKey)==="shown")return;
  voyagerWarningShowing=true;
  window.localStorage.setItem(storageKey,"shown");
  try{
    await showInfoModal("Предчувствие",warning.text||`Кажется, что работа ${warning.work_label||"Х"} сегодня приведет к гибели ${warning.victim_name||"Y"}, Сообщать об этом ему или нет - ваше решение`,{
      iconSrc:"/photo/work_room/hinthidden.png",
      iconAlt:"Предупреждение Вояжера"
    });
    await apiPost("/api/game/voyager-warning-ack",{user_id:currentUserId(),event_id:eventId});
  }finally{voyagerWarningShowing=false;}
}

let clayPopupShowing=false;
async function handleClayPopup(popup=null){
  const eventId=Number(popup?.id||0);
  if(!eventId||clayPopupShowing)return;
  clayPopupShowing=true;
  try{
    await showInfoModal(popup.title||"Глиняная статуя",popup.text||"Вы получили Глиняную статую.",{
      iconSrc:"/photo/work_room/neutralresult.png",
      iconAlt:"Глиняная статуя"
    });
    await apiPost("/api/game/clay-popup-ack",{user_id:currentUserId(),event_id:eventId});
  }finally{clayPopupShowing=false;}
}

async function handleBloodbotEvent(event=null){
  const eventId=Number(event?.id||0);
  if(!eventId)return;
  const storageKey=`bloodbot-event:${currentUserId()}:${eventId}`;
  if(window.localStorage.getItem(storageKey)==="shown")return;
  window.localStorage.setItem(storageKey,"shown");
  await showInfoModal(event.dead?"Механизм разрушен":"Механизм слабеет",event.text||"Состояние механизма изменилось.",{
    iconSrc:"/photo/work_room/133button.png",
    iconAlt:"Кровавый механизм"
  });
  if(event.psychosis)await handleMentalEvents({psychosis:event.psychosis,heart_attack:event.psychosis?.heart_attack});
}

async function applyGameState(payload, options = {}) {
  const game = payload?.game || {};
  const anomalies = payload?.anomalies || [];
  const turnUi = payload?.turn_ui || {};
  const brainrot = payload?.brainrot_music || {};
  if (brainrot.active && Array.isArray(brainrot.tracks) && brainrot.tracks.length) {
    if (Number(brainrot.day || 0) !== brainrotMusicDay || !brainrotMusicUrl) {
      brainrotMusicDay = Number(brainrot.day || 0);
      brainrotMusicUrl = brainrot.tracks[Math.floor(Math.random() * brainrot.tracks.length)];
    }
  }
  if (!game.started) {
    lastAppliedTurnOwnerId = null;
    renderGameActionLog([]);
    return false;
  }
  handleSoftlockVote(payload?.softlock_vote);
  const activeGameStartedAt = Number(payload?.core?.started_at || payload?.lobby?.game_started_at || 0);
  if (activeGameStartedAt && lastActiveGameStartedAt && activeGameStartedAt !== lastActiveGameStartedAt) {
    closeEventModal();
    gameFinalScreen.classList.add("hidden");
    activeTennaGame = null;
    tennaOverlay?.classList.add("hidden");
    tennaMini?.classList.add("hidden");
    activePo3Event = null;
    po3RenderedSignature = "";
    document.getElementById("po3EventOverlay")?.classList.add("hidden");
  }
  if (activeGameStartedAt) lastActiveGameStartedAt = activeGameStartedAt;
  const sharedMultiplayerEvent = !!(payload?.tenna_game?.active || payload?.po3_event?.active);
  if (sharedMultiplayerEvent) stopSpectatorCamera();
  if (payload?.tenna_game?.active) {
    renderTennaGame(payload.tenna_game);
  } else if (activeTennaGame) {
    activeTennaGame = null;
    tennaOverlay?.classList.add("hidden");
    tennaMini?.classList.add("hidden");
  }
  if (payload?.po3_event?.active) {
    renderPo3Event(payload.po3_event);
  } else if (activePo3Event) {
    renderPo3Event({active:false}, true);
    po3RenderedSignature = "";
  }

  stopOnlinePolling();
  onlineScreen.classList.add("hidden");
  gameScreen.classList.remove("hidden");
  renderTurnRibbon(turnUi);
  // The Voyager warning belongs to the very start of the foretold day and
  // must be shown before other queued day events.
  await handleVoyagerWarning(payload?.voyager_warning);
  await handleClayPopup(payload?.clay_popup);
  await handleTrainTicketState(payload?.train_ticket);
  handleViolinButtonState(payload?.violin_button);
  await handleBrassSphereEvent(payload?.brass_sphere_event);
  await handleX125Events(payload?.x125_events);
  await handleX125SpecialEvent(payload?.x125_special_event);
  await handleKlipotaEvent(payload?.klipota_event);
  await handleBloodbotEvent(payload?.bloodbot_event);
  const utilizerNoticeWasShown = await showUtilizerNoticeIfPending(payload?.utilizer_notice);
  if (utilizerNoticeWasShown) {
    // The user may keep this modal open while newer polling responses arrive.
    // Never continue rendering the stale pre-confirmation payload: reload the
    // authoritative turn after the notice has been acknowledged.
    const refreshedGame = await api(`/api/game?user_id=${encodeURIComponent(currentUserId())}`);
    return applyGameState(refreshedGame, { ...options, forceRefresh: true });
  }
  if (payload?.contract_summary?.pending) {
    await showContractSummaryIfPending(payload.contract_summary);
    return true;
  }
  if (payload?.target_notice?.pending) {
    if (!targetNoticeShowing) {
      targetNoticeShowing = true;
      try {
        await showInfoModal(
          payload.target_notice.title || "Воздействие другого игрока",
          payload.target_notice.message || "Другой игрок выбрал вас целью."
        );
        await apiPost("/api/game/target-notice-ack", {
          user_id: currentUserId(),
          notice_id: payload.target_notice.id
        });
      } finally {
        targetNoticeShowing = false;
      }
    }
    return true;
  }

  const currentTurnOwnerId = String(turnUi.current_turn_user_id || "");
  const isMyTurn = !!turnUi.is_my_turn;
  if (turnUi.is_alive === false) {
    // A dead player must never remain inside their old interactive room or
    // hint screen. Keep the global death dialog available, then let the next
    // camera render place them into spectator mode.
    closeDetailsEventModal();
    gameRoomScreen.classList.add("hidden");
    gameDetailsScreen.classList.add("hidden");
    activeRoomPayload = null;
    activeRoomAnomalyId = null;
    currentDetailsPayload = null;
  }
  const becameMyTurn = isMyTurn && !sameUserId(lastAppliedTurnOwnerId, currentUserId());
  lastAppliedTurnOwnerId = currentTurnOwnerId || null;
  const signature = `${game.current_day}:${game.day_started_at || ""}`;
  const shouldShowDayOverlay = options.forceRefresh || activeGameSignature !== signature;
  renderGameActionLog(isMyTurn ? [] : (payload?.action_log || []));
  if (gameSurrenderButton) gameSurrenderButton.disabled = turnUi.is_alive === false;
  const nextSelectionKey = anomalies.map((item) => String(item.id)).join("|");

  if (isMyTurn && payload?.d20_roll_pending && !options.skipD20) {
    await handleD20CurseRoll();
    return true;
  }

  if (isMyTurn && payload?.crimson_bite?.pending && !options.skipCrimson) {
    await handleCrimsonBite(payload.crimson_bite);
    return true;
  }

  if (!isMyTurn && !sharedMultiplayerEvent) {
    activeGameSignature = signature;
    activeGameSelectionKey = nextSelectionKey;
    await showSpectatorCamera(payload?.camera_view || {});
    return true;
  }

  if (!isMyTurn || !anomalies.length) {
    activeGameSignature = signature;
    activeGameSelectionKey = nextSelectionKey;
    if (!sharedMultiplayerEvent) showWaitingState(turnUi);
    return true;
  }

  const wasSpectating = spectatorMode;
  stopSpectatorCamera();

  // renderWorkRoom/renderDetailsScreen also fill the regular local screen while
  // showing another player's camera.  Never carry that observed state into our
  // own newly-started turn: it would make the other player's anomaly look ours.
  if (wasSpectating || becameMyTurn) {
    activeRoomPayload = null;
    activeRoomAnomalyId = null;
    currentDetailsPayload = null;
    activeGameAnomalies = [];
    activeGameSelectionKey = "";
    gameRoomScreen.classList.add("hidden");
    gameDetailsScreen.classList.add("hidden");
  }

  gameWaitingScreen.classList.add("hidden");
  if (!options.forceRefresh && !wasSpectating && !becameMyTurn && (gameRoomScreen && !gameRoomScreen.classList.contains("hidden"))) {
    activeGameSignature = signature;
    activeGameSelectionKey = nextSelectionKey;
    return true;
  }
  if (!options.forceRefresh && !wasSpectating && !becameMyTurn && (gameDetailsScreen && !gameDetailsScreen.classList.contains("hidden"))) {
    activeGameSignature = signature;
    activeGameSelectionKey = nextSelectionKey;
    return true;
  }
  if (!shouldShowDayOverlay) {
    if (activeGameSelectionKey !== nextSelectionKey || gameSelectScreen.classList.contains("hidden")) {
      renderGameSelection(anomalies);
    }
    try {
      if (!x125AudioLock && !sovuhVnActive) ensureGameMusic(brainrot.active ? "brainrot" : "selection").play().catch(() => {});
    } catch (_) {}
    gameSelectScreen.classList.remove("hidden");
    gameRoomScreen.classList.add("hidden");
    if (payload?.alastor_task?.pending) {
      window.setTimeout(() => {
        if (!gameSelectScreen.classList.contains("hidden") && vnOverlay.classList.contains("hidden")) {
          showAlastorTaskFromGameStateIfPending(payload).catch((error) => showRuntimeErrorModal(error));
        }
      }, 80);
    }
    return true;
  }

  activeGameSignature = signature;
  activeGameSelectionKey = nextSelectionKey;
  gameDayText.textContent = `ДЕНЬ ${game.current_day}`;
  gameDayOverlay.classList.remove("hidden");
  gameSelectScreen.classList.add("hidden");
  gameWaitingScreen.classList.add("hidden");
  try {
    if (!x125AudioLock && !sovuhVnActive) await ensureGameMusic(brainrot.active ? "brainrot" : "selection").play();
  } catch (_) {}
  window.setTimeout(() => {
    renderGameSelection(anomalies);
    gameDayOverlay.classList.add("hidden");
    gameSelectScreen.classList.remove("hidden");
    gameRoomScreen.classList.add("hidden");
    if (payload?.alastor_task?.pending) {
      window.setTimeout(() => {
        if (!gameSelectScreen.classList.contains("hidden") && vnOverlay.classList.contains("hidden")) {
          showAlastorTaskFromGameStateIfPending(payload).catch((error) => showRuntimeErrorModal(error));
        }
      }, 80);
    }
  }, 1400);
  return true;
}

function ensureGamePolling() {
  if (gameStatePoller) return;
  gameStatePoller = window.setInterval(async () => {
    if (gameScreen.classList.contains("hidden") || gameStatePollBusy) return;
    gameStatePollBusy = true;
    try {
      const payload = await api(`/api/game?user_id=${currentUserId()}`);
      await handleTrainTicketState(payload?.train_ticket);
      await handleBrassSphereEvent(payload?.brass_sphere_event);
      if (!payload?.game?.started) {
        if (deferFinalResultsModal) {
          return;
        }
        stopGamePolling();
        if (showFinalResults(payload?.final_results)) {
          return;
        }
        closeGameScreen();
        onlineScreen.classList.remove("hidden");
        openOnlineRoomView();
        await loadOnlineLobby();
        return;
      }
      await applyGameState(payload);
    } catch (_) {
    } finally {
      gameStatePollBusy = false;
    }
  }, 1500);
}

async function openGameSequence() {
  try {
    await apiPost("/api/game/train-pause", { user_id: currentUserId(), paused: false });
  } catch (_) {}
  const payload = await api(`/api/game?user_id=${currentUserId()}`);
  await handleTrainTicketState(payload?.train_ticket);
  await handleBrassSphereEvent(payload?.brass_sphere_event);
  const opened = await applyGameState(payload);
  if (opened) {
    ensureGamePolling();
  }
}

function updateDetails(item) {
  if (!item.is_done) {
    codexDetails.classList.remove("empty");
    codexDetails.innerHTML = `
      <img class="codex-large-photo" src="/photo/web_ui/nophoto.png" alt="неизвестно">
      <div class="codex-detail-row"><span>Имя:</span> <strong>неизвестно</strong></div>
      <div class="codex-detail-row"><span>Класс:</span> <strong>неизвестно</strong></div>
      <div class="codex-detail-row"><span>Тип:</span> <strong>неизвестно</strong></div>
      <div class="codex-description-title">Описание:</div>
      <p class="codex-description">неизвестно</p>
    `;
    return;
  }
  const className = classMap[item.class_id] || "неизвестно";
  const typeName = typeMap[item.type_id] || "неизвестно";
  const meta = classMeta[className] || null;
  const iconMarkup = meta ? `<img class="risk-icon" src="${meta.icon}" alt="${className}">` : "";
  const classCss = meta ? meta.cssClass : "";
  codexDetails.classList.remove("empty");
  codexDetails.innerHTML = `
    <img class="codex-large-photo" src="${item.photo}" alt="${item.name}">
    <div class="codex-detail-row"><span>Имя:</span> <strong>${item.name}</strong></div>
    <div class="codex-detail-row codex-class-row"><span>Класс:</span> ${iconMarkup}<strong class="${classCss}">${className}</strong></div>
    <div class="codex-detail-row"><span>Тип:</span> <strong>${typeName}</strong></div>
    <div class="codex-description-title">Описание:</div>
    <p class="codex-description">${item.description}</p>
  `;
}

function attachWorkButtonSound(button, handler) {
  button.addEventListener("click", (...args) => {
    if (button.dataset.placeholderButton === "true") return;
    playSound("workButton");
    handler(...args);
  });
}

function getStripColor(item) {
  if (!item.is_done) return "rgb(99, 99, 94)";
  return classMeta[classMap[item.class_id]]?.strip || "rgb(99, 99, 94)";
}

function getStripClass(label) {
  if (label.length > 18) return "xlong";
  if (label.length > 12) return "long";
  return "";
}

function formatStripLabel(label) {
  if (label.length > 18) return `${label.slice(0, 15)}...`;
  if (label.length > 12) return `${label.slice(0, 11)}...`;
  return label;
}

function renderCodexPage() {
  const start = (currentPage - 1) * itemsPerPage;
  const pageItems = codexItems.slice(start, start + itemsPerPage);
  codexGrid.innerHTML = pageItems.map((item) => `
    <article class="codex-card" data-item-id="${item.id}" tabindex="0">
      <div class="codex-strip ${getStripClass(item.name)}" style="background:${getStripColor(item)}" title="${item.name}">${formatStripLabel(item.name)}</div>
      <img class="codex-photo" src="${item.is_done ? item.photo : "/photo/web_ui/nophoto.png"}" alt="${item.name}">
    </article>
  `).join("");
  pageIndicator.textContent = `${currentPage} / ${totalPages}`;
  pagePrev.disabled = currentPage === 1;
  pageNext.disabled = currentPage === totalPages;
  clearDetails();
  codexGrid.querySelectorAll(".codex-card").forEach((card, index) => {
    const item = pageItems[index];
    const selectCard = () => {
      codexGrid.querySelectorAll(".codex-card").forEach((entry) => entry.classList.remove("selected"));
      card.classList.add("selected");
      updateDetails(item);
    };
    card.addEventListener("click", selectCard);
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectCard();
      }
    });
  });
}

async function ensureCodexLoaded() {
  if (codexLoaded) return;
  const payload = await api(`/api/codex?user_id=${currentUserId()}`);
  codexItems = payload.entries;
  totalPages = Math.max(1, Math.ceil(codexItems.length / itemsPerPage));
  codexProgressValue.textContent = `${payload.percent}%`;
  codexLoaded = true;
}

function leaderboardAvatarMarkup(entry) {
  if (entry.AVATAR_URL) {
    return `<img src="${entry.AVATAR_URL}" alt="${entry.NAME}">`;
  }
  return "?";
}

function renderLeaderboard(entries, page, total) {
  leaderboardList.innerHTML = entries.map((entry, index) => {
    const rank = (page - 1) * 10 + index + 1;
    return `
      <article class="leaderboard-row">
        <div class="leaderboard-rank">${rank}.</div>
        <div class="leaderboard-avatar">${leaderboardAvatarMarkup(entry)}</div>
        <div class="leaderboard-text">${entry.NAME} - ${Number(entry.CP).toLocaleString('ru-RU')} очков</div>
      </article>
    `;
  }).join("");
  leaderboardIndicator.textContent = `${page} / ${total}`;
  leaderboardPrev.disabled = page === 1;
  leaderboardNext.disabled = page === total;
}

async function loadLeaderboard(page = 1) {
  const payload = await api(`/api/leaderboard?page=${page}&per_page=10`);
  leaderboardPage = payload.page;
  leaderboardTotalPages = payload.total_pages;
  renderLeaderboard(payload.entries || [], payload.page, payload.total_pages);
}

async function loadProfile() {
  const payload = await api("/api/me");
  discordOauthEnabled = !!payload.oauth_enabled;
  debugModeEnabled = !!payload.debug_enabled;
  document.querySelectorAll(".debug-only").forEach((element) => {
    element.classList.toggle("hidden", !debugModeEnabled);
  });
  document.querySelectorAll(".player-status-only").forEach((element) => {
    element.classList.toggle("hidden", debugModeEnabled);
  });
  if (payload.discord_user?.id) {
    updateProfile(payload.discord_user);
    return;
  }
  updateProfile(null);
}

async function openLeaderboard() {
  await loadLeaderboard(leaderboardPage);
  leaderboardScreen.classList.remove("hidden");
  toast.classList.remove("visible");
}

async function openCodex() {
  await ensureCodexLoaded();
  codexScreen.classList.remove("hidden");
  toast.classList.remove("visible");
  renderCodexPage();
}

function closeCodex() { clearAndHide(codexScreen); }
function closeLeaderboard() { clearAndHide(leaderboardScreen); }

placeholderButtons.forEach((button) => button.addEventListener("click", () => showToast(button.dataset.placeholder)));
playOpenButton.addEventListener("click", () => openPlayScreen().catch((error) => showRuntimeErrorModal(error)));
playBackButton.addEventListener("click", closePlayScreen);
onlineModeButton.addEventListener("click", () => openOnlineScreen().catch((error) => showRuntimeErrorModal(error)));
createLobbyButton.addEventListener("click", () => createLobby().catch((error) => showRuntimeErrorModal(error)));
onlineBackButton.addEventListener("click", () => {
  if (!onlineRoomView.classList.contains("hidden")) {
    openOnlineListView();
    loadOnlineLobby().catch(() => {});
    return;
  }
  closeOnlineScreen();
  playScreen.classList.remove("hidden");
});
gameRoomBack.addEventListener("click", () => {
  finishPreviewActive = false;
  closeInventoryModal();
  closeStatUpgradeModal();
  gameRoomScreen.classList.add("hidden");
  gameSelectScreen.classList.remove("hidden");
  resetRoomResultGrid();
});
gameRoomName.addEventListener("click", () => openDetailsScreen().catch((error) => showRuntimeErrorModal(error)));
Object.entries(workButtonMap()).forEach(([workType, button]) => {
  attachWorkButtonSound(button, () => startWorkFlow(workType));
});
attachWorkButtonSound(actionWorkButton, openWorkMenu);
attachWorkButtonSound(actionWorkBackButton, openActionMenu);
attachWorkButtonSound(actionRiskBackButton, openWorkMenu);
attachWorkButtonSound(actionTypeBackButton, openRiskMenu);
attachWorkButtonSound(actionInventoryButton, () => openInventoryModal().catch((error) => showRuntimeErrorModal(error)));
attachWorkButtonSound(actionFleeButton, () => fleeWorkAction().catch((error) => showRuntimeErrorModal(error)));
attachWorkButtonSound(actionFinishButton, () => finishWorkAction().catch((error) => showRuntimeErrorModal(error)));
attachWorkButtonSound(actionArtifactButton, () => openProtocolXTargetChoice().catch((error) => showRuntimeErrorModal(error)));
attachWorkButtonSound(actionViolinButton, () => showToast("Украсть скрипку"));
actionRepeatWorkButton.addEventListener("click", () => {
  playSound("workButton");
  if (selectedWorkType) runWork(selectedWorkType);
});
attachWorkButtonSound(actionChangeWorkButton, openWorkMenu);
attachWorkButtonSound(actionReturnMenuButton, openActionMenu);
statUpgradeList.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-stat-upgrade]");
  if (!button || upgradeModalBusy) return;
  playSound("workButton");
  upgradeModalBusy = true;
  try {
    await upgradeStat(button.dataset.statUpgrade);
  } catch (error) {
    await showRuntimeErrorModal(error);
  } finally {
    upgradeModalBusy = false;
  }
});
statUpgradeCloseButton.addEventListener("click", async () => {
  if (upgradeModalBusy) return;
  playSound("workButton");
  upgradeModalBusy = true;
  try {
    await confirmFinishTurn();
  } catch (error) {
    await showRuntimeErrorModal(error);
  } finally {
    upgradeModalBusy = false;
  }
});
inventoryCloseButton?.addEventListener("click", () => {
  playSound("workButton");
  closeInventoryModal();
});
inventoryUseButton?.addEventListener("click", async () => {
  if (inventoryUseButton.disabled || inventoryUseBusy) return;
  playSound("workButton");
  try {
    await useInventoryItem();
  } catch (error) {
    await showRuntimeErrorModal(error);
  }
});
eventConfirmButton.addEventListener("click", closeEventModal);
detailsEventConfirmButton.addEventListener("click", closeDetailsEventModal);
trainTicketButton?.addEventListener("click", async () => {
  if (trainTicketButton.disabled) return;
  trainTicketButton.disabled = true;
  try {
    const payload = await apiPost("/api/game/train-ticket", { user_id: currentUserId() });
    playSound("trainSell");
    await handleTrainTicketState(payload.train_ticket);
    showInfoToast(payload.message || "Таймер поезда сброшен!");
  } catch (error) {
    showRuntimeErrorModal(error);
  } finally {
    trainTicketButton.disabled = false;
  }
});
violinStealButton?.addEventListener("click", async () => {
  if (violinStealButton.disabled) return;
  violinStealButton.disabled = true;
  try {
    const payload = await apiPost("/api/game/violin-steal", { user_id: currentUserId() });
    handleViolinButtonState(payload.violin_button);
    if (payload.wave_triggered) {
      playSound("damageHit");
      triggerDamageFlash();
    }
    if (payload.player_dead) {
      await showDeathModal(payload.death_reason || "Погиб от беззвучной волны скрипки");
      if (showFinalResults(payload.final_results || payload.game_state?.final_results)) return;
      if (payload.game_state?.game?.started) {
        await applyGameState(payload.game_state, { forceRefresh: true });
      }
      return;
    }
    await showInfoModal(
      payload.wave_triggered ? "Беззвучная волна" : "Скрипка украдена",
      payload.message || "Вы украли скрипку.",
      { iconSrc: "/photo/special/skripka.png", iconAlt: "Скрипка" }
    );
  } catch (error) {
    await showRuntimeErrorModal(error);
  } finally {
    violinStealButton.disabled = false;
  }
});
window.addEventListener("pagehide", () => {
  if (!currentTrainTicketState?.paused) return;
  const body = JSON.stringify({ user_id: currentUserId(), paused: false });
  navigator.sendBeacon("/api/game/train-pause", new Blob([body], { type: "application/json" }));
});
vnCloseButton.addEventListener("click", closeVnModal);
adminAddStatsButton.addEventListener("click", () => adminAction("add_stats").catch((error) => showRuntimeErrorModal(error)));
adminAddRpButton.addEventListener("click", () => adminAction("add_rp").catch((error) => showRuntimeErrorModal(error)));
adminRollPsychosisButton.addEventListener("click", () => adminAction("roll_psychosis").catch((error) => showRuntimeErrorModal(error)));
adminTrainTenSecondsButton.addEventListener("click", () => adminAction("train_10_seconds").catch((error) => showRuntimeErrorModal(error)));
adminX125Button.addEventListener("click", () => adminAction("x125_random_task").catch((error) => showRuntimeErrorModal(error)));
adminSetDayButton.addEventListener("click", () => {
  if (!adminDayInput.value) return;
  adminAction("set_day", Number(adminDayInput.value)).catch((error) => showRuntimeErrorModal(error));
});
adminSpawnAnomalyButton.addEventListener("click", () => {
  if (!adminAnomalyInput.value) return;
  adminAction("spawn_anomaly", Number(adminAnomalyInput.value)).catch((error) => showRuntimeErrorModal(error));
});
adminForceNextAnomalyButton.addEventListener("click", () => {
  if (!adminNextAnomalyInput.value) return;
  adminAction("force_next_anomaly", Number(adminNextAnomalyInput.value)).catch((error) => showRuntimeErrorModal(error));
});
adminForceD20RollButton?.addEventListener("click", () => {
  if (!adminD20RollInput?.value) return;
  adminAction("force_d20_roll", Number(adminD20RollInput.value)).catch((error) => showRuntimeErrorModal(error));
});
adminForceAlastorTaskButton?.addEventListener("click", () => {
  if (!adminAlastorTaskInput?.value) return;
  adminAction("force_alastor_task", Number(adminAlastorTaskInput.value)).catch((error) => showRuntimeErrorModal(error));
});
gameFinalCloseButton.addEventListener("click", () => {
  closeGameScreen();
  closeOnlineScreen();
  closePlayScreen();
});
gameMusicToggle?.addEventListener("click", toggleGameMusic);
gameSurrenderButton?.addEventListener("click", openSurrenderConfirmation);
updateGameMusicToggle();
gameDetailsCloseButton.addEventListener("click", () => {
  closeDetailsScreen(true).catch(() => {});
});
gameDetailsLightboxClose.addEventListener("click", () => {
  gameDetailsLightbox.classList.add("hidden");
});
gameDetailsLightbox.addEventListener("click", (event) => {
  if (event.target === gameDetailsLightbox) {
    gameDetailsLightbox.classList.add("hidden");
  }
});
document.querySelectorAll("[data-risk-choice]").forEach((button) => {
  button.addEventListener("click", () => {
    playSound("workButton");
    setRiskChoice(button.dataset.riskChoice);
  });
});
document.querySelectorAll("[data-type-choice]").forEach((button) => {
  button.addEventListener("click", () => {
    playSound("workButton");
    setTypeChoice(button.dataset.typeChoice);
  });
});
codexOpenButton.addEventListener("click", () => openCodex().catch((error) => showRuntimeErrorModal(error)));
codexCloseButton.addEventListener("click", closeCodex);
leaderboardOpenButton.addEventListener("click", () => openLeaderboard().catch((error) => showRuntimeErrorModal(error)));
leaderboardBackButton.addEventListener("click", closeLeaderboard);
leaderboardPrev.addEventListener("click", () => { if (leaderboardPage > 1) loadLeaderboard(leaderboardPage - 1).catch((error) => showRuntimeErrorModal(error)); });
leaderboardNext.addEventListener("click", () => { if (leaderboardPage < leaderboardTotalPages) loadLeaderboard(leaderboardPage + 1).catch((error) => showRuntimeErrorModal(error)); });
pagePrev.addEventListener("click", () => { if (currentPage > 1) { currentPage -= 1; renderCodexPage(); } });
pageNext.addEventListener("click", () => { if (currentPage < totalPages) { currentPage += 1; renderCodexPage(); } });
profileButton.addEventListener("click", () => {
  if (!discordUser?.id) {
    if (discordOauthEnabled) window.location.href = "/auth/discord/login";
    return;
  }
  profileMenu.classList.toggle("hidden");
});
profileLogout.addEventListener("click", () => {
  profileMenu.classList.add("hidden");
  window.location.href = "/auth/discord/logout";
});

document.addEventListener("click", (event) => {
  if (!event.target.closest("#profileShell")) profileMenu.classList.add("hidden");
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const softlockOverlay = document.getElementById("softlockOverlay");
    if (softlockOverlay && !softlockOverlay.classList.contains("hidden")) {
      event.preventDefault();
      return;
    }
    if (!gameScreen.classList.contains("hidden")) {
      event.preventDefault();
      requestSoftlockVote();
      return;
    }
    if (!onlineScreen.classList.contains("hidden")) {
      if (!onlineRoomView.classList.contains("hidden")) {
        openOnlineListView();
        loadOnlineLobby().catch(() => {});
      } else {
        closeOnlineScreen();
        if (discordUser) playScreen.classList.remove("hidden");
      }
    }
    if (!playScreen.classList.contains("hidden")) closePlayScreen();
    if (!codexScreen.classList.contains("hidden")) closeCodex();
    if (!leaderboardScreen.classList.contains("hidden")) closeLeaderboard();
    profileMenu.classList.add("hidden");
  }
});

loadProfile().catch(() => {
  updateProfile(null);
});

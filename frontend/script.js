function renderRecipes(recipes) {
  const cards = document.getElementById('cards');
  cards.innerHTML = '';
  recipes.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'card';
    if (r.image_url) {
      card.style.backgroundImage = `url(${r.image_url})`;
    }
    const ingredients = Array.isArray(r.ingredients) ? r.ingredients : [];
    const steps = Array.isArray(r.instructions) ? r.instructions : [];
    const stepsText = steps.map((s,i) => `${i+1}. ${s}`).join('\n');
    const safeTitle = (r.title || 'Recipe').replace(/"/g,'');
    // Generate a unique recipe_id from title (or use provided recipe_id)
    const recipeId = r.recipe_id || safeTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const isFavourite = userFavourites.has(recipeId);
    const favouriteBtnClass = isFavourite ? 'btn-favourite active' : 'btn-favourite';
    const favouriteBtnText = isFavourite ? '❤️ Favourited' : '🤍 Favourite';
    
      card.innerHTML = `
      <h2>${safeTitle}</h2>
      <div class="ingredients-and-image">
        <div class="ingredients-col">
          <p><strong>Ingredients</strong></p>
          <ul class="ingredients-list">
            ${ingredients.map((s)=>`<li class="ingredient-chip">${s}</li>`).join('')}
          </ul>
        </div>
        ${r.image_url ? `<img class="recipe-thumb" src="${r.image_url}" alt="${safeTitle}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='blog.jpg'">` : `<img class="recipe-thumb" src="placeholder.svg" alt="${safeTitle}" loading="lazy">`}
      </div>
      <div class="instructions-section">
        <h3>Instructions</h3>
        <div class="instruction-translate-controls">
          <span class="instruction-translate-label">🌐 Language</span>
          <select id="lang-${recipeId}" class="instruction-language-select">
            <option value="en" selected>English</option>
            <option value="hi">हिंदी</option>
            <option value="mr">मराठी</option>
          </select>
          <span class="instructions-translation-status" aria-live="polite"></span>
        </div>
        <ol class="instructions-list">
          ${steps.map((s)=>`<li>${s}</li>`).join('')}
        </ol>
      </div>
      <div class="actions">
        ${isAuthenticated ? `<button class="btn ${favouriteBtnClass}" data-recipe-id="${recipeId}" data-recipe-name="${safeTitle}" data-recipe-image="${r.image_url || ''}">${favouriteBtnText}</button>` : ''}
        <button class="btn btn-primary listen-btn">🔊 Listen</button>
        <button class="btn btn-secondary stop-btn">⏹️ Stop</button>
        <a class="btn btn-youtube" href="${r.video_url}" target="_blank" rel="noopener" aria-label="Watch on YouTube">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="margin-right:6px"><path d="M23.5 6.2c-.3-1.3-1.3-2.3-2.6-2.6C18.9 3 12 3 12 3s-6.9 0-8.9.6C1.8 4 0.8 5 0.5 6.3 0 8.3 0 12 0 12s0 3.7.5 5.8c.3 1.3 1.3 2.3 2.6 2.6 2 .6 8.9.6 8.9.6s6.9 0 8.9-.6c1.3-.3 2.3-1.3 2.6-2.6.5-2.1.5-5.8.5-5.8s0-3.7-.5-5.8zM9.6 15.5v-7l6.2 3.5-6.2 3.5z"></path></svg>
          Watch on YouTube
        </a>
      </div>
    `;
    const ListenBtn = card.querySelector('.listen-btn');
    const stopBtn = card.querySelector('.stop-btn');
    const favouriteBtn = card.querySelector('.btn-favourite');
    const langSelect = card.querySelector('.instruction-language-select');
    const instructionsList = card.querySelector('.instructions-list');
    const translationStatus = card.querySelector('.instructions-translation-status');
    if (favouriteBtn) {
      // Store full recipe data in button for favouriting
      favouriteBtn.dataset.recipeData = JSON.stringify(r);
      favouriteBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent card click
        toggleFavourite(recipeId, safeTitle, r.image_url || '', r, favouriteBtn);
      });
    }
    if (langSelect && instructionsList) {
      attachInstructionTranslationControls({
        recipeId,
        recipeTitle: safeTitle,
        steps,
        selectEl: langSelect,
        listEl: instructionsList,
        statusEl: translationStatus,
        listenBtn: ListenBtn,
        stopBtn: stopBtn
      });
    }
    cards.appendChild(card);
  });
}

// --- UI: Ingredients chips ---
const state = {
  ingredients: []
};

function renderChips() {
  const wrap = document.getElementById('chips');
  const count = document.getElementById('ing-count');
  if (!wrap) return;
  wrap.innerHTML = '';
  state.ingredients.forEach((name, i) => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.innerHTML = `${name} <button aria-label="remove">×</button>`;
    chip.querySelector('button').addEventListener('click', () => {
      state.ingredients.splice(i,1);
      renderChips();
    });
    wrap.appendChild(chip);
  });
  if (count) count.textContent = state.ingredients.length ? `${state.ingredients.length} ingredients selected` : '';
}

// Modify addIngredientFromInput to check suggestions
function addIngredientFromInput() {
  const input = document.getElementById('ingredients');
  if (!input) return;
  const value = (input.value || '').trim();
  if (!value) return;

  // Check if suggestions are shown
  const ul = document.getElementById('suggestions-list');
  const items = ul ? ul.querySelectorAll('li') : [];
  if (ul && ul.style.display === 'block' && items.length > 0) {
    // Don't add partial entries if suggestions are present! (Slack-like behavior)
    // Unless exact match;
    for (let i = 0; i < items.length; i++) {
      if ((items[i].textContent || '').toLowerCase() === value.toLowerCase()) {
        state.ingredients.push(items[i].textContent);
        input.value = '';
        renderChips();
        clearSuggestions();
        return;
      }
    }
    // If it's a partial entry and suggestions exist, don't add now.
    return;
  }
  // No relevant suggestions, allow free-form add
  state.ingredients.push(value);
  input.value = '';
  renderChips();
}

// --- UI: Dropdowns ---
function setupDropdown(id) {
  const root = document.getElementById(id);
  if (!root) return { get: () => '' };
  const toggle = root.querySelector('.dropdown-toggle');
  const menu = root.querySelector('.dropdown-menu');
  toggle.addEventListener('click', () => root.classList.toggle('open'));
  menu.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const label = btn.textContent.trim();
    const val = btn.getAttribute('data-value') || '';
    toggle.textContent = label;
    toggle.setAttribute('data-value', val);
    root.classList.remove('open');
  });
  return {
    get: () => toggle.getAttribute('data-value') || ''
  };
}

let cuisineSelect, mealSelect;
let isAuthenticated = false;
let userFavourites = new Set(); // Track favourite recipe IDs
let currentUserId = null;

// --- Voice input (Web Speech API) ---
let voiceRecognition = null;
let isVoiceListening = false;

// Keep original instructions per recipe so we can switch languages without losing them
const originalInstructionsByRecipeId = new Map();
// Cache translated instructions per recipe and language (e.g. { hi: [...], mr: [...] })
const translatedInstructionsByRecipeId = new Map();

// --- Text-to-Speech helpers for recipe instructions ---

function getSpeechLangCode(targetLang) {
  if (targetLang === 'hi') return 'hi-IN';
  if (targetLang === 'mr') return 'mr-IN';
  return 'en-US';
}

function pickVoiceForLang(targetLang) {
  if (!('speechSynthesis' in window)) return null;
  const desiredLang = getSpeechLangCode(targetLang);
  const voices = window.speechSynthesis.getVoices() || [];
  if (!voices.length) return null;

  // Prefer exact language match
  let voice = voices.find(v => v.lang === desiredLang);
  if (voice) return voice;
  // Then fallback to prefix match (e.g., hi, mr)
  const prefix = desiredLang.split('-')[0];
  voice = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(prefix));
  if (voice) return voice;
  // Fallback to any default voice
  return voices.find(v => v.default) || voices[0] || null;
}

function speakInstructionsText(text, targetLang) {
  if (!('speechSynthesis' in window)) {
    alert('Text-to-speech is not supported in this browser.');
    return;
  }
  try {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const langCode = getSpeechLangCode(targetLang);
    utterance.lang = langCode;
    const voice = pickVoiceForLang(targetLang);
    if (voice) {
      utterance.voice = voice;
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.error('TTS error:', e);
  }
}

function setupVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('Web Speech API SpeechRecognition not supported in this browser.');
    const micBtn = document.getElementById('voice-input-btn');
    if (micBtn) {
      micBtn.style.display = 'none';
    }
    return;
  }

  const micBtn = document.getElementById('voice-input-btn');
  const statusEl = document.getElementById('voice-status');
  const inputEl = document.getElementById('ingredients');
  if (!micBtn || !inputEl) return;

  const recognition = new SpeechRecognition();
  recognition.lang = navigator.language || 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.continuous = false;

  voiceRecognition = recognition;

  function updateStatus(listening, message) {
    isVoiceListening = listening;
    if (statusEl) {
      statusEl.style.display = listening ? 'inline' : 'none';
      if (message) statusEl.textContent = message;
    }
    if (micBtn) {
      if (listening) {
        micBtn.classList.add('active');
      } else {
        micBtn.classList.remove('active');
      }
    }
  }

  micBtn.addEventListener('click', () => {
    if (!voiceRecognition) return;
    if (isVoiceListening) {
      try {
        voiceRecognition.stop();
      } catch (e) {
        console.error('Error stopping recognition:', e);
      }
      return;
    }
    try {
      voiceRecognition.start();
    } catch (e) {
      // Can throw if called too quickly
      console.error('Error starting recognition:', e);
    }
  });

  recognition.onstart = () => {
    updateStatus(true, 'Listening…');
  };

  recognition.onend = () => {
    updateStatus(false);
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event);
    updateStatus(false);
    if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
      alert('Microphone access was blocked. Please allow mic permissions in your browser settings and try again.');
    } else if (event.error === 'no-speech') {
      alert('No speech was detected. Please try speaking again.');
    }
  };

  recognition.onresult = (event) => {
    if (!event.results || !event.results[0] || !event.results[0][0]) return;
    const transcript = event.results[0][0].transcript || '';
    if (!transcript.trim()) return;

    // Split into ingredients by commas and the word "and"
    const pieces = transcript
      .split(/,| and /i)
      .map(p => p.trim())
      .filter(Boolean);

    const newText = pieces.join(', ');
    if (!newText) return;

    const current = (inputEl.value || '').trim();
    inputEl.value = current ? `${current}, ${newText}` : newText;
  };
}

// --- Instructions translation helper functions ---

function updateInstructionsList(listEl, steps) {
  if (!listEl) return;
  const safeSteps = Array.isArray(steps) ? steps : [];
  listEl.innerHTML = safeSteps.map((s) => `<li>${s}</li>`).join('');
}

async function requestInstructionTranslation(steps, targetLang) {
  const res = await fetch('http://localhost:5000/translate_instructions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      instructions: steps,
      target_lang: targetLang
    })
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || `Translation failed with status ${res.status}`);
  }
  if (!Array.isArray(data.instructions)) {
    throw new Error('Translation response is missing instructions list.');
  }
  return data.instructions;
}

function attachInstructionTranslationControls({ recipeId, recipeTitle, steps, selectEl, listEl, statusEl, listenBtn, stopBtn }) {
  if (!selectEl || !listEl) return;

  const baseSteps = Array.isArray(steps) ? steps.slice() : [];
  originalInstructionsByRecipeId.set(recipeId, baseSteps);

  const languageLabels = {
    en: 'English',
    hi: 'Hindi',
    mr: 'Marathi'
  };

  // Helper to build the spoken text for the current language
  function buildSpokenTextForLang(lang) {
    let stepsForLang;
    if (lang === 'en') {
      stepsForLang = originalInstructionsByRecipeId.get(recipeId) || baseSteps;
    } else {
      const perRecipe = translatedInstructionsByRecipeId.get(recipeId) || {};
      stepsForLang = perRecipe[lang];
      // Fallback to what is currently rendered if cache is missing
      if (!stepsForLang && listEl) {
        stepsForLang = Array.from(listEl.querySelectorAll('li')).map(li => li.textContent || '');
      }
    }
    const safeSteps = Array.isArray(stepsForLang) ? stepsForLang : [];
    return safeSteps.map((s, i) => `${i + 1}. ${s}`).join('. ');
  }

  selectEl.addEventListener('change', async (e) => {
    const targetLang = (e.target.value || 'en').toLowerCase();

    // Reset to original English without hitting the backend
    if (targetLang === 'en') {
      const original = originalInstructionsByRecipeId.get(recipeId) || baseSteps;
      updateInstructionsList(listEl, original);
      if (statusEl) statusEl.textContent = '';
      return;
    }

    const original = originalInstructionsByRecipeId.get(recipeId) || baseSteps;
    if (!original.length) return;

    if (statusEl) {
      statusEl.textContent = `Translating to ${languageLabels[targetLang] || targetLang}…`;
    }
    selectEl.disabled = true;

    try {
      const translated = await requestInstructionTranslation(original, targetLang);
      updateInstructionsList(listEl, translated);
      // Cache translated steps for later voice playback or quick switching
      const existing = translatedInstructionsByRecipeId.get(recipeId) || {};
      existing[targetLang] = translated.slice();
      translatedInstructionsByRecipeId.set(recipeId, existing);
      if (statusEl) {
        statusEl.textContent = `Showing ${languageLabels[targetLang] || targetLang} translation`;
      }
    } catch (err) {
      console.error('Instruction translation failed:', err);
      alert('Could not translate instructions. Please try again.');
      // Revert select back to English on failure
      selectEl.value = 'en';
      const fallback = originalInstructionsByRecipeId.get(recipeId) || baseSteps;
      updateInstructionsList(listEl, fallback);
      if (statusEl) statusEl.textContent = '';
    } finally {
      selectEl.disabled = false;
    }
  });

  if (listenBtn) {
    listenBtn.addEventListener('click', () => {
      const currentLang = (selectEl.value || 'en').toLowerCase();
      const text = buildSpokenTextForLang(currentLang);
      if (!text) return;
      speakInstructionsText(`${recipeTitle}. ${text}`, currentLang);
    });
  }

  if (stopBtn) {
    stopBtn.addEventListener('click', () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    });
  }
}

// Check authentication status
async function checkAuthStatus() {
  try {
    const res = await fetch('http://localhost:5000/check-auth', {
      method: 'GET',
      credentials: 'include' // Important for cookies/sessions
    });
    const data = await res.json();
    
    if (data.authenticated) {
      isAuthenticated = true;
      currentUserId = data.user_id;
      document.getElementById('auth-buttons').style.display = 'none';
      document.getElementById('user-info').style.display = 'flex';
      document.getElementById('user-name-display').textContent = `Welcome, ${data.user_name}!`;
      // Fetch user's favourites on login
      await fetchFavourites();
    } else {
      isAuthenticated = false;
      currentUserId = null;
      userFavourites.clear();
      document.getElementById('auth-buttons').style.display = 'flex';
      document.getElementById('user-info').style.display = 'none';
    }
  } catch (err) {
    console.error('Auth check failed:', err);
    isAuthenticated = false;
    currentUserId = null;
    userFavourites.clear();
    document.getElementById('auth-buttons').style.display = 'flex';
    document.getElementById('user-info').style.display = 'none';
  }
}

// Logout function
async function logout() {
  try {
    await fetch('http://localhost:5000/logout', {
      method: 'POST',
      credentials: 'include'
    });
    userFavourites.clear();
    currentUserId = null;
    window.location.reload();
  } catch (err) {
    console.error('Logout failed:', err);
    userFavourites.clear();
    currentUserId = null;
    window.location.reload();
  }
}

// Favourite Recipes Functions

async function fetchFavourites() {
  if (!isAuthenticated) return;
  
  try {
    const res = await fetch('http://localhost:5000/favourites', {
      method: 'GET',
      credentials: 'include'
    });
    
    if (res.ok) {
      const data = await res.json();
      userFavourites.clear();
      data.favourites.forEach(fav => {
        userFavourites.add(fav.recipe_id);
      });
      // Update favourite buttons if recipes are displayed
      updateFavouriteButtons();
    }
  } catch (err) {
    console.error('Failed to fetch favourites:', err);
  }
}

async function toggleFavourite(recipeId, recipeName, recipeImage, fullRecipeData, buttonElement) {
  if (!isAuthenticated) {
    alert('Please sign in to add favourites.');
    window.location.href = 'http://localhost:5000/login';
    return;
  }
  
  const isFavourite = userFavourites.has(recipeId);
  
  try {
    if (isFavourite) {
      // Remove from favourites
      const url = `http://localhost:5000/favourites/${encodeURIComponent(recipeId)}`;
      console.log('Removing favourite:', url);
      
      const res = await fetch(url, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      console.log('Delete response status:', res.status);
      
      if (res.ok) {
        userFavourites.delete(recipeId);
        buttonElement.textContent = '🤍 Favourite';
        buttonElement.classList.remove('active');
        // Update favourites display if visible
        if (document.getElementById('favourites-section')) {
          await fetchFavourites();
          renderFavourites();
        }
      } else {
        let errorMsg = 'Unknown error';
        try {
          const data = await res.json();
          errorMsg = data.error || 'Unknown error';
        } catch (e) {
          errorMsg = `HTTP ${res.status}: ${res.statusText}`;
        }
        console.error('Failed to remove favourite:', errorMsg);
        alert('Failed to remove favourite: ' + errorMsg);
      }
    } else {
      // Add to favourites
      // Ensure we have the full recipe data structure
      const recipeDataToStore = fullRecipeData || {
        title: recipeName,
        ingredients: [],
        instructions: [],
        image_url: recipeImage,
        video_url: `https://www.youtube.com/results?search_query=${encodeURIComponent(recipeName + ' recipe')}`
      };
      
      const requestBody = {
        recipe_id: recipeId,
        recipe_name: recipeName,
        recipe_image: recipeImage,
        recipe_data: recipeDataToStore  // Store full recipe data
      };
      console.log('Adding favourite with data:', requestBody);
      console.log('Full recipe data:', recipeDataToStore);
      
      const res = await fetch('http://localhost:5000/favourites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });
      
      console.log('POST response status:', res.status);
      
      if (res.ok || res.status === 201) {
        userFavourites.add(recipeId);
        buttonElement.textContent = '❤️ Favourited';
        buttonElement.classList.add('active');
      } else if (res.status === 409) {
        // Already favourited
        userFavourites.add(recipeId);
        buttonElement.textContent = '❤️ Favourited';
        buttonElement.classList.add('active');
      } else {
        let errorMsg = 'Unknown error';
        try {
          const data = await res.json();
          errorMsg = data.error || 'Unknown error';
        } catch (e) {
          errorMsg = `HTTP ${res.status}: ${res.statusText}`;
        }
        console.error('Failed to add favourite:', errorMsg, 'Status:', res.status);
        alert('Failed to add favourite: ' + errorMsg);
      }
    }
  } catch (err) {
    console.error('Favourite toggle failed:', err);
    console.error('Error details:', {
      message: err.message,
      stack: err.stack,
      recipeId: recipeId,
      recipeName: recipeName
    });
    alert('Failed to update favourite: ' + (err.message || 'Network error. Please check if the backend server is running.'));
  }
}

function updateFavouriteButtons() {
  document.querySelectorAll('.btn-favourite').forEach(btn => {
    const recipeId = btn.getAttribute('data-recipe-id');
    if (userFavourites.has(recipeId)) {
      btn.textContent = '❤️ Favourited';
      btn.classList.add('active');
    } else {
      btn.textContent = '🤍 Favourite';
      btn.classList.remove('active');
    }
  });
}

async function renderFavourites() {
  if (!isAuthenticated) {
    return;
  }
  
  try {
    const res = await fetch('http://localhost:5000/favourites', {
      method: 'GET',
      credentials: 'include'
    });
    
    if (!res.ok) {
      console.error('Failed to fetch favourites');
      return;
    }
    
    const data = await res.json();
    console.log('Fetched favourites:', data);
    
    const favouritesSection = document.getElementById('favourites-section');
    
    if (!favouritesSection) return;
    
    const favouritesContainer = document.getElementById('favourites-container');
    if (!favouritesContainer) return;
    
    favouritesContainer.innerHTML = '';
    
    if (data.favourites.length === 0) {
      favouritesContainer.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No favourite recipes yet. Add some recipes to your favourites!</p>';
      return;
    }
    
    data.favourites.forEach(fav => {
      console.log('Processing favourite:', fav);
      console.log('Recipe data:', fav.recipe_data);
      const card = document.createElement('div');
      card.className = 'card favourite-card';
      card.style.cursor = 'pointer';
      if (fav.recipe_image) {
        card.style.backgroundImage = `url(${fav.recipe_image})`;
      }
      
      // Make card clickable to show details
      card.addEventListener('click', (e) => {
        // Don't trigger if clicking the favourite button
        if (e.target.closest('.btn-favourite')) {
          return;
        }
        showRecipeDetails(fav);
      });
      
      card.innerHTML = `
        <h2 style="cursor: pointer;">${fav.recipe_name}</h2>
        <p style="color: #666; font-size: 14px; margin-top: 10px;">Click to view full recipe details</p>
        <div class="actions">
          <button class="btn btn-favourite active" data-recipe-id="${fav.recipe_id}" data-recipe-name="${fav.recipe_name}" data-recipe-image="${fav.recipe_image || ''}">❤️ Favourited</button>
        </div>
      `;
      
      const favouriteBtn = card.querySelector('.btn-favourite');
      if (favouriteBtn) {
        favouriteBtn.addEventListener('click', (e) => {
          e.stopPropagation(); // Prevent card click
          const fullRecipe = fav.recipe_data || null;
          toggleFavourite(fav.recipe_id, fav.recipe_name, fav.recipe_image || '', fullRecipe, favouriteBtn);
          // Remove card from display after unfavouriting
          setTimeout(() => {
            if (!userFavourites.has(fav.recipe_id)) {
              card.remove();
              if (favouritesContainer.children.length === 0) {
                favouritesContainer.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No favourite recipes yet. Add some recipes to your favourites!</p>';
              }
            }
          }, 100);
        });
      }
      
      favouritesContainer.appendChild(card);
    });
  } catch (err) {
    console.error('Failed to render favourites:', err);
  }
}

function showFavouritesPage() {
  const mainSection = document.querySelector('.bg-section');
  const favouritesSection = document.getElementById('favourites-section');
  
  if (favouritesSection) {
    mainSection.style.display = 'none';
    favouritesSection.style.display = 'block';
    renderFavourites();
  }
}

function showMainPage() {
  const mainSection = document.querySelector('.bg-section');
  const favouritesSection = document.getElementById('favourites-section');
  
  if (favouritesSection) {
    mainSection.style.display = 'block';
    favouritesSection.style.display = 'none';
  }
}

function showRecipeDetails(fav) {
  // Get recipe data (either from recipe_data field or construct from available data)
  let recipe = fav.recipe_data;
  
  console.log('Favourite data:', fav);
  console.log('Recipe data:', recipe);
  console.log('Recipe data type:', typeof recipe);
  
  // If recipe_data is a string (JSON), parse it
  if (typeof recipe === 'string') {
    try {
      recipe = JSON.parse(recipe);
      console.log('Parsed recipe data:', recipe);
    } catch (e) {
      console.error('Failed to parse recipe_data:', e);
      recipe = null;
    }
  }
  
  // If no recipe_data, show a message that this is an old favourite
  if (!recipe || (!recipe.ingredients && !recipe.instructions)) {
    console.warn('No recipe_data found or empty data');
    // Show alert and suggest re-favouriting
    const shouldContinue = confirm(
      'This favourite was added before we started storing full recipe details. ' +
      'To see ingredients and instructions, please:\n\n' +
      '1. Remove this favourite\n' +
      '2. Generate the recipe again\n' +
      '3. Add it to favourites again\n\n' +
      'Click OK to continue viewing (limited details) or Cancel to go back.'
    );
    
    if (!shouldContinue) {
      return;
    }
    
    recipe = {
      title: fav.recipe_name,
      ingredients: [],
      instructions: [],
      image_url: fav.recipe_image,
      video_url: `https://www.youtube.com/results?search_query=${encodeURIComponent(fav.recipe_name + ' recipe')}`
    };
  }
  
  // Handle both possible data structures
  const ingredients = Array.isArray(recipe.ingredients) ? recipe.ingredients : 
                     (recipe.ingredients ? [recipe.ingredients] : []);
  const steps = Array.isArray(recipe.instructions) ? recipe.instructions : 
               (recipe.instructions ? [recipe.instructions] : []);
  
  console.log('Final Ingredients:', ingredients);
  console.log('Final Steps:', steps);
  
  const stepsText = steps.map((s,i) => `${i+1}. ${s}`).join('\n');
  const safeTitle = (recipe.title || fav.recipe_name).replace(/"/g,'');
  const recipeId = fav.recipe_id || safeTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  const isFavourite = userFavourites.has(recipeId);
  const favouriteBtnClass = isFavourite ? 'btn-favourite active' : 'btn-favourite';
  const favouriteBtnText = isFavourite ? '❤️ Favourited' : '🤍 Favourite';
  
  // Create modal overlay with exact same structure as regular recipe cards
  const modal = document.createElement('div');
  modal.className = 'recipe-modal-overlay';
  modal.innerHTML = `
    <div class="recipe-modal-content">
      <button class="recipe-modal-close" onclick="this.closest('.recipe-modal-overlay').remove()">&times;</button>
      <div class="recipe-modal-body">
        <div class="card" style="box-shadow: none; background: transparent;">
          <h2>${safeTitle}</h2>
          <div class="ingredients-and-image">
            <div class="ingredients-col">
              <p><strong>Ingredients</strong></p>
              <ul class="ingredients-list">
                ${ingredients.length > 0 ? ingredients.map((s)=>`<li class="ingredient-chip">${s}</li>`).join('') : '<li class="ingredient-chip" style="color: #999;">No ingredients available</li>'}
              </ul>
            </div>
            ${recipe.image_url || fav.recipe_image ? `<img class="recipe-thumb" src="${recipe.image_url || fav.recipe_image}" alt="${safeTitle}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='blog.jpg'">` : `<img class="recipe-thumb" src="placeholder.svg" alt="${safeTitle}" loading="lazy">`}
          </div>
          <div class="instructions-section">
            <h3>Instructions</h3>
            <div class="instruction-translate-controls">
              <span class="instruction-translate-label">🌐 Language</span>
              <select id="lang-${recipeId}-modal" class="instruction-language-select">
                <option value="en" selected>English</option>
                <option value="hi">हिंदी</option>
                <option value="mr">मराठी</option>
              </select>
              <span class="instructions-translation-status" aria-live="polite"></span>
            </div>
            <ol class="instructions-list">
              ${steps.length > 0 ? steps.map((s)=>`<li>${s}</li>`).join('') : '<li style="color: #999;">No instructions available</li>'}
            </ol>
          </div>
          <div class="actions">
            ${isAuthenticated ? `<button class="btn ${favouriteBtnClass}" data-recipe-id="${recipeId}" data-recipe-name="${safeTitle}" data-recipe-image="${recipe.image_url || fav.recipe_image || ''}">${favouriteBtnText}</button>` : ''}
            <button class="btn btn-primary listen-btn">🔊 Listen</button>
            <button class="btn btn-secondary stop-btn">⏹️ Stop</button>
            <a class="btn btn-youtube" href="${recipe.video_url || `https://www.youtube.com/results?search_query=${encodeURIComponent(safeTitle + ' recipe')}`}" target="_blank" rel="noopener" aria-label="Watch on YouTube">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="margin-right:6px"><path d="M23.5 6.2c-.3-1.3-1.3-2.3-2.6-2.6C18.9 3 12 3 12 3s-6.9 0-8.9.6C1.8 4 0.8 5 0.5 6.3 0 8.3 0 12 0 12s0 3.7.5 5.8c.3 1.3 1.3 2.3 2.6 2.6 2 .6 8.9.6 8.9.6s6.9 0 8.9-.6c1.3-.3 2.3-1.3 2.6-2.6.5-2.1.5-5.8.5-5.8s0-3.7-.5-5.8zM9.6 15.5v-7l6.2 3.5-6.2 3.5z"></path></svg>
              Watch on YouTube
            </a>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add to page
  document.body.appendChild(modal);
  
  // Add event listeners - same as regular recipe cards
  const listenBtn = modal.querySelector('.listen-btn');
  const stopBtn = modal.querySelector('.stop-btn');
  const favouriteBtn = modal.querySelector('.btn-favourite');
  const langSelect = modal.querySelector('.instruction-language-select');
  const instructionsList = modal.querySelector('.instructions-list');
  const translationStatus = modal.querySelector('.instructions-translation-status');
  if (favouriteBtn) {
    favouriteBtn.dataset.recipeData = JSON.stringify(recipe);
    favouriteBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleFavourite(recipeId, safeTitle, recipe.image_url || fav.recipe_image || '', recipe, favouriteBtn);
      // Update button state after toggle
      setTimeout(() => {
        const isFav = userFavourites.has(recipeId);
        favouriteBtn.textContent = isFav ? '❤️ Favourited' : '🤍 Favourite';
        favouriteBtn.classList.toggle('active', isFav);
      }, 100);
    });
  }

  if (langSelect && instructionsList) {
    attachInstructionTranslationControls({
      recipeId,
      recipeTitle: safeTitle,
      steps,
      selectEl: langSelect,
      listEl: instructionsList,
      statusEl: translationStatus,
      listenBtn: listenBtn,
      stopBtn: stopBtn
    });
  }
  
  // Close on overlay click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
  
  // Close on Escape key
  const closeHandler = (e) => {
    if (e.key === 'Escape') {
      modal.remove();
      document.removeEventListener('keydown', closeHandler);
    }
  };
  document.addEventListener('keydown', closeHandler);
}

document.addEventListener('DOMContentLoaded', () => {
  checkAuthStatus();
  const addBtn = document.getElementById('add-ingredient');
  if (addBtn) addBtn.addEventListener('click', addIngredientFromInput);
  const input = document.getElementById('ingredients');
  if (input) input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); addIngredientFromInput(); } });
  cuisineSelect = setupDropdown('cuisine-dropdown');
  mealSelect = setupDropdown('meal-dropdown');
  // Set up microphone-based voice input for ingredients
  setupVoiceInput();
});

async function generateRecipe() {
  const inputVal = document.getElementById('ingredients').value;
  const ingredients = state.ingredients.length ? state.ingredients.join(', ') : inputVal;
  const output = document.getElementById('output');
  const loader = document.getElementById('loader');
  const cards = document.getElementById('cards');
  const cuisine = cuisineSelect ? cuisineSelect.get() : 'all';
  const meal = mealSelect ? mealSelect.get() : '';

  output.style.display = 'none';
  output.textContent = '';
  loader.style.display = 'block';
  cards.innerHTML = '';

  try {
    const res = await fetch('http://localhost:5000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Important for session cookies
      body: JSON.stringify({ ingredients, cuisine, meal })
    });
    
    const data = await res.json();
    loader.style.display = 'none';

    if (Array.isArray(data.recipes)) {
      renderRecipes(data.recipes);
    } else if (data.error) {
      output.style.display = 'block';
      output.textContent = 'Error: ' + data.error;
    } else {
      output.style.display = 'block';
      output.textContent = 'Unexpected response';
    }
  } catch (err) {
    loader.style.display = 'none';
    output.style.display = 'block';
    output.textContent = 'Error connecting to backend!';
  }
}

function ListenText(text) {
  if (!('speechSynthesis' in window)) {
    alert('Speech is not supported in this browser.');
    return;
  }
  try {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = navigator.language || 'en-US';
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.error('Speech error:', e);
  }
}

function stopListening() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

let suggestionIndex = -1;
let lastQuery = '';
let justSelectedByClick = false;

async function fetchIngredientSuggestions(query) {
  if (!query) return [];
  try {
    const res = await fetch(`http://localhost:5000/suggest_ingredients?q=${encodeURIComponent(query)}`, {
      credentials: 'include' // Important for session cookies
    });
    if (!res.ok) return [];
    const list = await res.json();
    return Array.isArray(list) ? list : [];
  } catch (e) {
    return [];
  }
}

async function searchRecipes(query) {
  if (!query || query.length < 2 || !isAuthenticated) return [];
  try {
    const res = await fetch(`http://localhost:5000/search?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      credentials: 'include'
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || [];
  } catch (e) {
    console.error('Recipe search error:', e);
    return [];
  }
}

function clearSuggestions() {
  const ul = document.getElementById('suggestions-list');
  if (!ul) return;
  ul.innerHTML = '';
  ul.style.display = 'none';
  suggestionIndex = -1;
}

async function showSuggestions(value) {
  const input = document.getElementById('ingredients');
  const ul = document.getElementById('suggestions-list');
  const val = (value || '').trim();
  ul.innerHTML = '';
  if (!val) {
    clearSuggestions();
    return;
  }
  lastQuery = val.toLowerCase();
  
  // Fetch both ingredient suggestions and recipe search results
  const [ingredientSuggestions, recipeResults] = await Promise.all([
    fetchIngredientSuggestions(val),
    searchRecipes(val)
  ]);
  
  if (lastQuery !== val.toLowerCase()) return; // input changed during fetch
  
  // Show recipe results first (if any), then ingredient suggestions
  let hasResults = false;
  
  // Add recipe results
  if (recipeResults.length > 0) {
    const recipeHeader = document.createElement('li');
    recipeHeader.className = 'suggestion-header';
    recipeHeader.textContent = '📜 Recipes';
    recipeHeader.style.cssText = 'font-weight: 600; color: #ff6a3d, #ff2e63 55%, #fd5da8; padding: 8px 12px; background: #f0f0f0; border-bottom: 1px solid #ddd; cursor: default;';
    ul.appendChild(recipeHeader);
    
    recipeResults.forEach((recipe, idx) => {
      const li = document.createElement('li');
      li.className = 'recipe-suggestion';
      li.dataset.recipeId = recipe.recipe_id;
      li.dataset.recipeData = JSON.stringify(recipe);
      
      const icon = recipe.source === 'favourites' ? '❤️' : '📜';
      li.innerHTML = `<span style="margin-right: 8px;">${icon}</span><span>${recipe.recipe_name}</span>`;
      li.style.cssText = 'padding: 10px 12px; cursor: pointer; display: flex; align-items: center;';
      
      if (idx === 0 && ingredientSuggestions.length === 0) {
        li.classList.add('selected');
        suggestionIndex = 0;
      }
      
      li.addEventListener('mousedown', function(event) {
        event.preventDefault();
        justSelectedByClick = true;
        openRecipeFromSearch(recipe);
        clearSuggestions();
        input.value = '';
      });
      
      li.addEventListener('mouseenter', function() {
        ul.querySelectorAll('li').forEach(l => l.classList.remove('selected'));
        this.classList.add('selected');
        suggestionIndex = Array.from(ul.querySelectorAll('li.recipe-suggestion, li.ingredient-suggestion')).indexOf(this);
      });
      
      ul.appendChild(li);
      hasResults = true;
    });
  }
  
  // Add ingredient suggestions
  if (ingredientSuggestions.length > 0) {
    if (recipeResults.length > 0) {
      const separator = document.createElement('li');
      separator.className = 'suggestion-separator';
      separator.style.cssText = 'padding: 4px; background: #f0f0f0; border-bottom: 1px solid #ddd;';
      ul.appendChild(separator);
    }
    
    const ingredientHeader = document.createElement('li');
    ingredientHeader.className = 'suggestion-header';
    ingredientHeader.textContent = '🥘 Ingredients';
    ingredientHeader.style.cssText = 'font-weight: 600; color: #ff6a3d; padding: 8px 12px; background: #f0f0f0; border-bottom: 1px solid #ddd; cursor: default;';
    ul.appendChild(ingredientHeader);
    
    ingredientSuggestions.forEach((item, idx) => {
      const li = document.createElement('li');
      li.className = 'ingredient-suggestion';
      li.textContent = item;
      
      const totalIndex = recipeResults.length + idx + (recipeResults.length > 0 ? 2 : 1);
      if (totalIndex === 0 || (recipeResults.length === 0 && idx === 0)) {
        li.classList.add('selected');
        suggestionIndex = 0;
      }
      
      li.addEventListener('mousedown', function(event) {
        justSelectedByClick = true;
        input.value = item;
        addIngredientFromInput();
        clearSuggestions();
        event.preventDefault(); // prevent blur
      });
      
      li.addEventListener('mouseenter', function() {
        ul.querySelectorAll('li').forEach(l => l.classList.remove('selected'));
        this.classList.add('selected');
        suggestionIndex = Array.from(ul.querySelectorAll('li.recipe-suggestion, li.ingredient-suggestion')).indexOf(this);
      });
      
      ul.appendChild(li);
      hasResults = true;
    });
  }
  
  if (!hasResults) {
    clearSuggestions();
    return;
  }
  
  ul.style.display = 'block';
  if (suggestionIndex < 0) suggestionIndex = 0;
}

function handleSuggestionKeys(e) {
  if (justSelectedByClick) {
    // Ignore Enter if just selected via click
    justSelectedByClick = false;
    return;
  }
  const ul = document.getElementById('suggestions-list');
  const items = ul ? ul.querySelectorAll('li.recipe-suggestion, li.ingredient-suggestion') : [];
  if (!items.length) return;
  if (e.key === 'ArrowDown') {
    items[suggestionIndex]?.classList.remove('selected');
    suggestionIndex = (suggestionIndex + 1) % items.length;
    items[suggestionIndex]?.classList.add('selected');
    e.preventDefault();
  } else if (e.key === 'ArrowUp') {
    items[suggestionIndex]?.classList.remove('selected');
    suggestionIndex = (suggestionIndex - 1 + items.length) % items.length;
    items[suggestionIndex]?.classList.add('selected');
    e.preventDefault();
  } else if (e.key === 'Enter') {
    const input = document.getElementById('ingredients');
    if (ul.style.display === 'block' && items.length > 0) {
      const selectedItem = items[suggestionIndex];
      if (selectedItem.classList.contains('recipe-suggestion')) {
        // It's a recipe - open it
        const recipeData = JSON.parse(selectedItem.dataset.recipeData);
        openRecipeFromSearch(recipeData);
        clearSuggestions();
        input.value = '';
      } else {
        // It's an ingredient - add it
        input.value = selectedItem.textContent;
        addIngredientFromInput();
        clearSuggestions();
      }
      e.preventDefault();
    }
  } else if (e.key === 'Escape') {
    clearSuggestions();
  }
}

function openRecipeFromSearch(recipeData) {
  // If it's a favourite with full data, show details
  if (recipeData.source === 'favourites' && recipeData.recipe_data) {
    showRecipeDetails({
      recipe_id: recipeData.recipe_id,
      recipe_name: recipeData.recipe_name,
      recipe_image: recipeData.recipe_image,
      recipe_data: recipeData.recipe_data
    });
  } else if (recipeData.source === 'favourites') {
    // Favourite but no data - fetch it from favourites
    fetch('http://localhost:5000/favourites', {
      method: 'GET',
      credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
      const fav = data.favourites.find(f => f.recipe_id === recipeData.recipe_id);
      if (fav) {
        showRecipeDetails(fav);
      } else {
        alert(`Recipe "${recipeData.recipe_name}" found in your favourites but full details are not available.`);
      }
    })
    .catch(err => {
      console.error('Error fetching favourite:', err);
      alert(`Recipe "${recipeData.recipe_name}" found in your favourites.`);
    });
  } else {
    // If it's from history, show a message
    alert(`Recipe "${recipeData.recipe_name}" found in your history.\n\n` +
          'This recipe is in your recipe history. Generate recipes again to see full details, or add it to favourites when you see it.');
  }
}

// Enhance DOMContentLoaded to wire up suggestions
(function enhanceSuggestions() {
  document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('ingredients');
    if (input) {
      input.setAttribute('autocomplete', 'off');
      input.addEventListener('input', (e) => showSuggestions(e.target.value));
      input.addEventListener('keydown', handleSuggestionKeys);
    }
    document.addEventListener('click', function(e) {
      const ul = document.getElementById('suggestions-list');
      if (!ul) return;
      if (e.target !== input && !ul.contains(e.target)) clearSuggestions();
    });
  });
})();

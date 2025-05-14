const emojis = ['🌟', '🚀', '🪐', '👽', '🛰️', '🌌', '🌍', '☄️'];
let cards = [...emojis, ...emojis];
let firstCard, secondCard;
let lockBoard = false;
let moves = 0;
let matchedPairs = 0;
let startTime;
let timerInterval;

const board = document.getElementById('game-board');
const movesDisplay = document.getElementById('moves');
const timerDisplay = document.getElementById('timer');

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function startGame() {
  board.innerHTML = '';
  shuffle(cards);
  moves = 0;
  matchedPairs = 0;
  movesDisplay.textContent = '🎯 Moves: 0';
  resetTimer();
  cards.forEach(emoji => {
    const card = document.createElement('div');
    card.classList.add('card');
    card.dataset.emoji = emoji;
    card.textContent = emoji;
    card.addEventListener('click', flipCard);
    card.style.color = 'transparent';
    board.appendChild(card);
  });
}

function flipCard() {
  if (lockBoard || this.classList.contains('flipped')) return;

  if (!startTime) startTimer();

  this.classList.add('flipped');
  this.style.color = '#000';

  if (!firstCard) {
    firstCard = this;
    return;
  }

  secondCard = this;
  lockBoard = true;
  moves++;
  movesDisplay.textContent = `🎯 Moves: ${moves}`;

  if (firstCard.dataset.emoji === secondCard.dataset.emoji) {
    matched();
  } else {
    mismatch();
  }
}

function matched() {
  firstCard.classList.add('match');
  secondCard.classList.add('match');
  resetFlip();
  matchedPairs++;

  if (matchedPairs === emojis.length) {
    clearInterval(timerInterval);
    const totalTime = Math.floor((Date.now() - startTime) / 1000);
    const isLoggedIn = document.cookie.includes('sessionid');

    if (isLoggedIn) {
      saveScore(moves, totalTime);
      alert(`🎉 You won in ${moves} moves and ${totalTime}s!\nYour score has been saved!`);
      window.location.href = '/scores/';
    } else {
      // Store score locally in browser
      localStorage.setItem('pendingScore', JSON.stringify({
        moves: moves,
        time_taken: totalTime
      }));

      // Redirect to login with next page pointing to score-saving page
      const wantsToLogin = confirm(`🎉 You won in ${moves} moves and ${totalTime}s!\n\nLogin to view your scores?`);
      if (wantsToLogin) {
        window.location.href = '/login/?next=/scores/';
      } else {
        window.location.href = '/signup/?next=/scores/';
      }
    }
  }
}

function saveScore(moves, totalTime) {
  const scoreData = {
    moves: moves,
    time_taken: totalTime
  };

  // Debugging: Log score data before sending it
  console.log('Sending score data:', scoreData);

 function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch('/save-score/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({ moves, time_taken: totalTime })

});

}

  
function mismatch() {
  firstCard.classList.add('mismatch');
  secondCard.classList.add('mismatch');
  setTimeout(() => {
    firstCard.classList.remove('flipped', 'mismatch');
    secondCard.classList.remove('flipped', 'mismatch');
    firstCard.style.color = 'transparent';
    secondCard.style.color = 'transparent';
    resetFlip();
  }, 1000);
}


function resetFlip() {
  [firstCard, secondCard] = [null, null];
  lockBoard = false;
}

function startTimer() {
  startTime = Date.now();
  timerInterval = setInterval(() => {
    const seconds = Math.floor((Date.now() - startTime) / 1000);
    timerDisplay.textContent = `⏱️ Time: ${seconds}s`;
  }, 1000);
}

function resetTimer() {
  clearInterval(timerInterval);
  startTime = null;
  timerDisplay.textContent = '⏱️ Time: 0s';
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}


function restartGame() {
  window.location.reload();
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

startGame();

document.addEventListener('DOMContentLoaded', function() {
  // The cameras array will be populated from the backend API
  let cameras = [];

  // Fetch camera data from the backend
  function fetchCameras() {
    fetch('/api/cameras')
      .then(response => response.json())
      .then(data => {
        cameras = data;
        renderCameras();
      })
      .catch(err => {
        console.error("Error fetching cameras:", err);
      });
  }

  // Update current time
  function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('current-time').textContent = timeString;
  }
  
  // Update time every second
  updateTime();
  setInterval(updateTime, 1000);

  // Render camera feeds dynamically
  function renderCameras() {
    const container = document.getElementById('camera-container');
    container.innerHTML = '';

    cameras.forEach(camera => {
      // Create camera card
      const card = document.createElement('div');
      card.className = 'camera-card';
      card.id = `camera-${camera.id}`;

      // Create camera feed element (using the stream URL from the camera object)
      const img = document.createElement('img');
      img.className = 'camera-feed';
      img.src = camera.stream_url ? camera.stream_url : `/placeholder.svg?height=480&width=640`;
      img.alt = `${camera.name} feed`;

      // Create camera info section
      const info = document.createElement('div');
      info.className = 'camera-info';

      const nameEl = document.createElement('div');
      nameEl.className = 'camera-name';
      nameEl.textContent = camera.name;

      const statusEl = document.createElement('div');
      statusEl.className = 'camera-status';

      const statusDot = document.createElement('div');
      statusDot.className = 'status-dot';
      if (camera.status !== 'online') {
        statusDot.style.backgroundColor = 'var(--danger)';
      }

      const statusText = document.createElement('span');
      statusText.textContent = camera.location;

      statusEl.appendChild(statusDot);
      statusEl.appendChild(statusText);

      info.appendChild(nameEl);
      info.appendChild(statusEl);

      // Create camera actions
      const actions = document.createElement('div');
      actions.className = 'camera-actions';

      const expandBtn = document.createElement('button');
      expandBtn.className = 'action-btn';
      expandBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>';
      expandBtn.title = 'Expand';
      expandBtn.onclick = () => expandCamera(camera.id);

      const recordBtn = document.createElement('button');
      recordBtn.className = 'action-btn';
      recordBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>';
      recordBtn.title = 'Record';

      const snapshotBtn = document.createElement('button');
      snapshotBtn.className = 'action-btn';
      snapshotBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>';
      snapshotBtn.title = 'Take Snapshot';

      actions.appendChild(expandBtn);
      actions.appendChild(recordBtn);
      actions.appendChild(snapshotBtn);

      // Assemble the camera card
      card.appendChild(img);
      card.appendChild(info);
      card.appendChild(actions);

      // Add the card to the container
      container.appendChild(card);
    });
  }

  // Expand camera to fullscreen
  function expandCamera(cameraId) {
    const card = document.getElementById(`camera-${cameraId}`);
    if (card.classList.contains('expanded')) {
      // Collapse if already expanded
      card.classList.remove('expanded');
      document.getElementById('camera-container').style.gridTemplateColumns = '';
    } else {
      // Collapse any previously expanded camera
      document.querySelectorAll('.camera-card.expanded').forEach(el => {
        el.classList.remove('expanded');
      });
      // Expand this camera
      card.classList.add('expanded');
      document.getElementById('camera-container').style.gridTemplateColumns = '1fr';
      // Scroll smoothly to the camera
      card.scrollIntoView({ behavior: 'smooth' });
    }
  }

  // Initialize the app by fetching camera data from the backend
  fetchCameras();

  // Handle refresh button click to reload cameras
  document.getElementById('refresh-btn').addEventListener('click', function() {
    fetchCameras();

    // Show a temporary notification
    const notification = document.createElement('div');
    notification.textContent = 'Cameras refreshed';
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.padding = '10px 20px';
    notification.style.backgroundColor = 'var(--success)';
    notification.style.color = 'white';
    notification.style.borderRadius = 'var(--border-radius)';
    notification.style.zIndex = '1000';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transition = 'opacity 0.5s ease';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 500);
    }, 2000);
  });

  // Handle fullscreen button click
  document.getElementById('fullscreen-btn').addEventListener('click', function() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  });

  // Simulate Alexa voice command suggestions
  const alexaCommands = [
    "Alexa, Show Camera one",
    "Alexa, Display all cameras",
    "Alexa, open cameras"
  ];

  // Randomly update the Alexa command suggestion every 10 seconds
  setInterval(() => {
    const randomCommand = alexaCommands[Math.floor(Math.random() * alexaCommands.length)];
    document.querySelector('.alexa-indicator span').textContent = `Try saying: "${randomCommand}"`;
  }, 10000);
});

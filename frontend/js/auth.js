/* IncidentOps-AI - Login page logic */

(function() {
  const form = document.getElementById('login-form');
  const errorBox = document.getElementById('login-error');
  const btn = document.getElementById('login-btn');

  if (!form) {
    console.warn('Login form not found');
    return;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
      showError('Please enter username and password');
      return;
    }

    errorBox.classList.remove('visible');
    btn.disabled = true;
    btn.textContent = 'Signing in...';

    try {
      await api.login(username, password);

      // CRITICAL: wait for Set-Cookie to be committed by the browser
      await new Promise(r => setTimeout(r, 300));

      // Verify the session actually works before navigating
      try {
        await api.me();
      } catch (probeErr) {
        // Session didn't stick - retry once more after a longer wait
        await new Promise(r => setTimeout(r, 500));
        await api.me();
      }

      const params = new URLSearchParams(window.location.search);
      const next = params.get('next') || '/';
      window.location.href = next;

    } catch (err) {
      console.error('Login error:', err);
      showError('Invalid username or password');
      btn.disabled = false;
      btn.textContent = 'Sign In';
      document.getElementById('password').value = '';
      document.getElementById('password').focus();
    }
  });

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.add('visible');
  }
})();

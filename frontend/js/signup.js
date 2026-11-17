/* IncidentOps-AI - Signup page logic */

(function () {
  const form = document.getElementById('signup-form');
  const errorBox = document.getElementById('signup-error');
  const btn = document.getElementById('signup-btn');

  if (!form) return;

  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[2]) : null;
  }

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.add('visible');
  }

  function clearError() {
    errorBox.textContent = '';
    errorBox.classList.remove('visible');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();

    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const password_confirm = document.getElementById('password_confirm').value;

    if (password !== password_confirm) {
      showError('Passwords do not match');
      return;
    }
    if (password.length < 8) {
      showError('Password must be at least 8 characters');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Creating account...';

    try {
      const headers = { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' };
      const csrf = getCookie('csrftoken');
      if (csrf) headers['X-CSRFToken'] = csrf;

      const res = await fetch('/api/auth/register/', {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({ username, email, password, password_confirm }),
      });

      const text = await res.text();
      let data = {};
      try { data = text ? JSON.parse(text) : {}; } catch (_) { data = { raw: text }; }

      if (res.status === 201) {
        // Success — brief success message, then redirect to login
        errorBox.textContent = '✅ Account created. Redirecting to login…';
        errorBox.style.background = 'rgba(34,197,94,.15)';
        errorBox.style.borderColor = 'rgba(34,197,94,.5)';
        errorBox.style.color = '#86efac';
        errorBox.classList.add('visible');
        setTimeout(() => { window.location.href = '/login/'; }, 900);
        return;
      }

      // Show field-level errors from DRF
      if (typeof data === 'object') {
        const firstError = Object.entries(data).map(([k, v]) => {
          const msg = Array.isArray(v) ? v.join(' ') : v;
          return k === 'non_field_errors' ? msg : `${k}: ${msg}`;
        }).join('\n');
        showError(firstError || 'Signup failed');
      } else {
        showError('Signup failed');
      }
    } catch (err) {
      console.error('Signup error:', err);
      showError('Network error — is the server running?');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Create account';
    }
  });
})();

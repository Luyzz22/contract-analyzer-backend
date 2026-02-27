/**
 * SSO User Integration
 * Lädt den User aus dem SSO Cookie und aktualisiert den Header
 */
(function() {
  // Parse JWT Token ohne Bibliothek
  function parseJwt(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  }

  // Cookie lesen
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  // User aus SSO Token laden
  function loadSSOUser() {
    const token = getCookie('sbs_auth_token');
    if (!token) return null;
    
    const payload = parseJwt(token);
    if (!payload) return null;
    
    // Token abgelaufen?
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      return null;
    }
    
    return {
      name: payload.name || payload.email?.split('@')[0] || 'User',
      email: payload.email || '',
      initials: getInitials(payload.name || payload.email || 'U')
    };
  }

  // Initialen berechnen
  function getInitials(name) {
    if (!name) return 'U';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  // Header aktualisieren
  function updateHeader(user) {
    if (!user) return;
    
    // Avatar
    const avatar = document.querySelector('.app-user-avatar');
    if (avatar) avatar.textContent = user.initials;
    
    // Name in Header
    const userName = document.querySelector('.app-user-name');
    if (userName) userName.textContent = user.name;
    
    // Name in User Menu
    const menuName = document.querySelector('.app-user-menu-name');
    if (menuName) menuName.textContent = user.name;
    
    // Email in User Menu
    const menuEmail = document.querySelector('.app-user-menu-email');
    if (menuEmail) menuEmail.textContent = user.email;
  }

  // Beim Laden ausführen
  document.addEventListener('DOMContentLoaded', function() {
    const user = loadSSOUser();
    if (user) {
      updateHeader(user);
    }
  });
})();

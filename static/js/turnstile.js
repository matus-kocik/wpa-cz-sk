// Cloudflare Turnstile callback
function turnstileCallback(token) {
  const input = document.querySelector('input[name="turnstile"]');
  if (input) {
    input.value = token;
  }
}

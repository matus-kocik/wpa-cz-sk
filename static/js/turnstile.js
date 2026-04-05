// Cloudflare Turnstile callback
function turnstileCallback(token) {
  const input = document.getElementById("turnstile-token");
  if (input) {
    input.value = token;
  }
}

document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobileMenuButton');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileLinks = mobileMenu.querySelectorAll('a');

    // Toggle menu
    mobileMenuButton.addEventListener('click', function () {
        mobileMenu.classList.toggle('hidden');
    });

    // Close menu on link click (only on mobile)
    mobileLinks.forEach(link => {
        link.addEventListener('click', function () {
            mobileMenu.classList.add('hidden');
        });
    });
});
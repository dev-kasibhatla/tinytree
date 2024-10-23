<script>
    document.addEventListener("DOMContentLoaded", function() {
        const links = document.querySelectorAll('.tt-link');

        links.forEach(link => {
            const url = link.querySelector('.tt-link-body').getAttribute('href');
            const faviconUrl = getFaviconUrl(url);
            link.querySelector('.tt-link-favicon').src = faviconUrl;
        });

        function getFaviconUrl(url) {
            const linkElement = document.createElement('a');
            linkElement.href = url;
            const baseUrl = linkElement.protocol + '//' + linkElement.host;
            return baseUrl + '/favicon.ico'; // Standard location for favicon
        }
    });
</script>
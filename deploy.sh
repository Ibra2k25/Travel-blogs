#!/bin/bash

# Discover Ghana Travel Website Deployment Script
# This script helps deploy the website to various hosting platforms

echo "🇬🇭 Discover Ghana - Deployment Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Project files found"

# Create a deployment directory
DEPLOY_DIR="dist"
if [ -d "$DEPLOY_DIR" ]; then
    echo "🗂️  Cleaning existing deployment directory..."
    rm -rf "$DEPLOY_DIR"
fi

echo "📁 Creating deployment directory..."
mkdir -p "$DEPLOY_DIR"

# Copy all necessary files
echo "📋 Copying files to deployment directory..."
cp index.html "$DEPLOY_DIR/"
cp styles.css "$DEPLOY_DIR/"
cp script.js "$DEPLOY_DIR/"
cp README.md "$DEPLOY_DIR/"

# Create a simple .htaccess file for Apache servers
echo "🔧 Creating .htaccess file..."
cat > "$DEPLOY_DIR/.htaccess" << 'EOF'
# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Enable browser caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com; font-src 'self' fonts.googleapis.com fonts.gstatic.com; img-src 'self' data: images.unsplash.com; connect-src 'self';"
</IfModule>

# Redirect to HTTPS
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</IfModule>
EOF

# Create a simple robots.txt
echo "🤖 Creating robots.txt..."
cat > "$DEPLOY_DIR/robots.txt" << 'EOF'
User-agent: *
Allow: /

Sitemap: https://yourdomain.com/sitemap.xml
EOF

# Create a basic sitemap.xml
echo "🗺️  Creating sitemap.xml..."
cat > "$DEPLOY_DIR/sitemap.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://yourdomain.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://yourdomain.com/#destinations</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://yourdomain.com/#packages</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://yourdomain.com/#culture</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://yourdomain.com/#book</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>
EOF

echo "✅ Deployment files created successfully!"
echo "📦 Files are ready in the '$DEPLOY_DIR' directory"
echo ""
echo "🚀 Deployment Options:"
echo "1. Upload the contents of '$DEPLOY_DIR' to your web server"
echo "2. Use FTP/SFTP to transfer files to your hosting provider"
echo "3. Deploy to GitHub Pages by pushing to a 'gh-pages' branch"
echo "4. Deploy to Netlify by dragging the '$DEPLOY_DIR' folder to netlify.com"
echo "5. Deploy to Vercel using 'vercel' command"
echo ""
echo "🌐 Don't forget to:"
echo "- Update the domain in sitemap.xml"
echo "- Configure your hosting provider's settings"
echo "- Test the deployed site thoroughly"
echo "- Set up SSL certificate"
echo ""
echo "🇬🇭 Happy deploying! Experience the Gateway to Africa!"
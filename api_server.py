from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

from monitor_service import get_monitor_service
from database import DatabaseManager
from config import Config

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Trump Monitor WhatsApp Client API",
    description="Web API for monitoring Donald Trump's social media activity",
    version="1.0.0"
)

# Pydantic models for API requests/responses
class StatusResponse(BaseModel):
    is_running: bool
    last_check: str = None
    check_interval_minutes: int
    platform_status: Dict[str, bool]
    statistics: Dict[str, Any]

class ManualCheckResponse(BaseModel):
    status: str
    message: str
    stats: Dict[str, Any] = None

class PostData(BaseModel):
    post_id: str
    platform: str
    content: str
    created_at: str
    url: str = None
    media_urls: str = None
    engagement_metrics: str = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trump Monitor WhatsApp Client</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #1e3a8a; text-align: center; }
            .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
            .running { background-color: #d1fae5; color: #065f46; }
            .stopped { background-color: #fee2e2; color: #991b1b; }
            .btn { background-color: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background-color: #2563eb; }
            .stats { background-color: #f8fafc; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .platform { margin: 5px 0; }
            .platform.online { color: #059669; }
            .platform.offline { color: #dc2626; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🇺🇸 Trump Monitor WhatsApp Client 🇺🇸</h1>
            
            <div id="status-container">
                <p>Loading status...</p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn" onclick="manualCheck()">🔍 Manual Check</button>
                <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
            </div>
            
            <div id="recent-posts">
                <h3>Recent Posts</h3>
                <div id="posts-container">Loading posts...</div>
            </div>
        </div>

        <script>
            async function fetchStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    
                    const statusClass = data.is_running ? 'running' : 'stopped';
                    const statusText = data.is_running ? '✅ Running' : '❌ Stopped';
                    
                    let platformsHtml = '<h4>Platform Status:</h4>';
                    for (const [platform, online] of Object.entries(data.platform_status)) {
                        const statusClass = online ? 'online' : 'offline';
                        const emoji = online ? '✅' : '❌';
                        platformsHtml += `<div class="platform ${statusClass}">${emoji} ${platform}</div>`;
                    }
                    
                    let statsHtml = '';
                    if (data.statistics.platform_stats) {
                        statsHtml += '<h4>Post Statistics:</h4>';
                        for (const [platform, count] of Object.entries(data.statistics.platform_stats)) {
                            statsHtml += `<div>• ${platform}: ${count} posts</div>`;
                        }
                        statsHtml += `<div>• Notifications sent: ${data.statistics.notifications_sent || 0}</div>`;
                    }
                    
                    document.getElementById('status-container').innerHTML = `
                        <div class="status ${statusClass}">
                            <h3>${statusText}</h3>
                            <p><strong>Check Interval:</strong> ${data.check_interval_minutes} minutes</p>
                            <p><strong>Last Check:</strong> ${data.last_check || 'Never'}</p>
                        </div>
                        <div class="stats">
                            ${platformsHtml}
                            ${statsHtml}
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('status-container').innerHTML = `<div class="status stopped">Error loading status: ${error}</div>`;
                }
            }
            
            async function fetchRecentPosts() {
                try {
                    const response = await fetch('/posts/recent?limit=5');
                    const posts = await response.json();
                    
                    if (posts.length === 0) {
                        document.getElementById('posts-container').innerHTML = '<p>No posts found.</p>';
                        return;
                    }
                    
                    let postsHtml = '';
                    posts.forEach(post => {
                        const date = new Date(post.created_at).toLocaleString();
                        postsHtml += `
                            <div style="border: 1px solid #e5e7eb; padding: 15px; margin: 10px 0; border-radius: 5px;">
                                <div style="font-weight: bold; color: #374151;">${post.platform} - ${date}</div>
                                <div style="margin: 10px 0;">${post.content.substring(0, 200)}${post.content.length > 200 ? '...' : ''}</div>
                                ${post.url ? `<div><a href="${post.url}" target="_blank">View Original</a></div>` : ''}
                            </div>
                        `;
                    });
                    
                    document.getElementById('posts-container').innerHTML = postsHtml;
                } catch (error) {
                    document.getElementById('posts-container').innerHTML = `<p>Error loading posts: ${error}</p>`;
                }
            }
            
            async function manualCheck() {
                try {
                    const response = await fetch('/manual-check', { method: 'POST' });
                    const result = await response.json();
                    alert(result.status === 'success' ? 'Manual check completed!' : `Error: ${result.message}`);
                    refreshStatus();
                } catch (error) {
                    alert(`Error: ${error}`);
                }
            }
            
            function refreshStatus() {
                fetchStatus();
                fetchRecentPosts();
            }
            
            // Load initial data
            refreshStatus();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshStatus, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current service status"""
    try:
        service = await get_monitor_service()
        status = service.get_status()
        return StatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/manual-check", response_model=ManualCheckResponse)
async def manual_check(background_tasks: BackgroundTasks):
    """Trigger a manual check for new posts"""
    try:
        service = await get_monitor_service()
        result = await service.manual_check()
        return ManualCheckResponse(**result)
    except Exception as e:
        logger.error(f"Error during manual check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/recent", response_model=List[PostData])
async def get_recent_posts(limit: int = 20, platform: str = None):
    """Get recent posts"""
    try:
        db = DatabaseManager()
        posts = db.get_recent_posts(platform=platform, limit=limit)
        return [PostData(**post) for post in posts]
    except Exception as e:
        logger.error(f"Error getting recent posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    """Get monitoring statistics"""
    try:
        db = DatabaseManager()
        stats = db.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start")
async def start_monitoring():
    """Start the monitoring service"""
    try:
        service = await get_monitor_service()
        if service.is_running:
            return {"status": "already_running", "message": "Service is already running"}
        
        success = await service.start_monitoring()
        if success:
            return {"status": "started", "message": "Monitoring service started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start monitoring service")
    except Exception as e:
        logger.error(f"Error starting service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
async def stop_monitoring():
    """Stop the monitoring service"""
    try:
        service = await get_monitor_service()
        if not service.is_running:
            return {"status": "already_stopped", "message": "Service is not running"}
        
        await service.stop_monitoring()
        return {"status": "stopped", "message": "Monitoring service stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Trump Monitor WhatsApp Client"}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}
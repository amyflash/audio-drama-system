-- 数据库初始化脚本（SQLite）
-- 极简广播剧管理与在线收听系统

-- ====================================
-- 1. 用户表 (users)
-- ====================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin', 'user')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    is_active BOOLEAN DEFAULT 1
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ====================================
-- 2. 专辑表 (albums)
-- ====================================
CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    cover_image VARCHAR(500) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    episode_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_albums_sort_order ON albums(sort_order);
CREATE INDEX IF NOT EXISTS idx_albums_created_at ON albums(created_at DESC);

-- ====================================
-- 3. 单集表 (episodes)
-- ====================================
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER DEFAULT 0,
    duration INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_episodes_album_id ON episodes(album_id);
CREATE INDEX IF NOT EXISTS idx_episodes_sort_order ON episodes(sort_order);

-- ====================================
-- 4. 会话审计表 (sessions) - 可选
-- ====================================
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- ====================================
-- 插入默认数据
-- ====================================

-- 插入默认管理员账号
-- 密码: 123456 (bcrypt 哈希)
-- 生产环境请立即修改密码！
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7YjwYqNqOe', 'admin')
ON CONFLICT(username) DO NOTHING;

-- ====================================
-- 创建视图（方便查询）
-- ====================================

-- 专辑详情视图（包含剧集统计）
CREATE VIEW IF NOT EXISTS album_detail AS
SELECT
    a.id,
    a.title,
    a.cover_image,
    a.description,
    a.sort_order,
    a.episode_count,
    a.created_at,
    a.updated_at,
    COALESCE(SUM(e.duration), 0) as total_duration
FROM albums a
LEFT JOIN episodes e ON a.id = e.album_id
GROUP BY a.id;

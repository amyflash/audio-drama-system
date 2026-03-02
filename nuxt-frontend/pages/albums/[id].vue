<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 pb-20 sm:pb-6">
    <!-- Toast 提示容器 -->
    <div v-if="toast.show" :style="{
      position: 'fixed',
      top: '20px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 9999,
      padding: '12px 24px',
      borderRadius: '8px',
      backgroundColor: toast.type === 'error' ? '#fee2e2' : toast.type === 'success' ? '#dcfce7' : '#fef3c7',
      color: toast.type === 'error' ? '#991b1b' : toast.type === 'success' ? '#166534' : '#92400e',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      animation: 'slideIn 0.3s ease-out'
    }">
      {{ toast.message }}
    </div>

    <!-- 移动端粘性顶部导航 -->
    <div style="background-color: white; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); border-bottom: 1px solid #e5e7eb; padding: 8px 16px; position: sticky; top: 0; z-index: 50; display: flex; align-items: center; justify-content: space-between;">
      <button
        @click="navigateTo('/')"
        style="color: #10b981; padding: 8px; font-size: 14px; font-weight: 500; border: none; background: none; cursor: pointer;"
      >
        ← 返回
      </button>
      <div style="display: flex; align-items: center; gap: 8px;">
        <button
          @click="navigateTo('/')"
          style="color: #3b82f6; padding: 6px 12px; font-size: 13px; font-weight: 500; border: 1px solid #3b82f6; background: white; border-radius: 6px; cursor: pointer; transition: background-color 0.2s;"
          onmouseover="this.style.backgroundColor='#eff6ff'"
          onmouseout="this.style.backgroundColor='white'"
        >
          登录设置
        </button>
        <div style="width: 32px; height: 32px; background: linear-gradient(to bottom right, #10b981, #059669); border-radius: 9999px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">
          {{ user?.username?.charAt(0).toUpperCase() || 'U' }}
        </div>
        <span style="font-size: 14px; color: #4b5563; max-width: 80px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
          {{ getUserDisplayName() }}
        </span>
      </div>
    </div>

    <div style="max-width: 80rem; margin: 0 auto; padding: 16px 24px;">
      <!-- 加载状态 - 骨架屏 -->
      <div v-if="loading" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 24px; margin-bottom: 24px;">
        <!-- 专辑信息骨架 -->
        <div style="display: flex; gap: 16px; margin-bottom: 24px;">
          <div
            style="width: 160px 192px; height: 160px 192px; flex-shrink: 0; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 12px; display: flex; align-items: center; justify-content: center;"
          >
            <span style="font-size: 48px; opacity: 0.3;">📚</span>
          </div>
          <div style="flex: 1;">
            <div
              style="height: 24px; width: 60%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px; margin-bottom: 12px;"
            ></div>
            <div
              style="height: 16px; width: 40%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px; margin-bottom: 8px;"
            ></div>
            <div
              style="height: 16px; width: 30%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px;"
            ></div>
          </div>
        </div>
        <!-- 单集列表骨架 x3 -->
        <div v-for="i in 3" :key="'episode-skeleton-' + i" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 16px;">
          <div
            style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; flex-shrink: 0;"
          ></div>
          <div style="flex: 1;">
            <div
              style="height: 18px; width: 70%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px; margin-bottom: 8px;"
            ></div>
            <div
              style="height: 14px; width: 30%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px;"
            ></div>
          </div>
          <div
            style="width: 40px; height: 36px; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 8px;"
          ></div>
        </div>
      </div>

      <!-- 专辑信息 - 移动端优化 -->
      <div v-else-if="album" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px 24px; margin-bottom: 24px;">
        
          <!-- 专辑信息 -->
          <div style="flex: 1; text-align: center; @media (min-width: 640px) { text-align: left; }">
            <h1 style="font-size: 24px 28px; font-weight: bold; color: #1f2937; margin-bottom: 8px;">{{ album.title }}</h1>
            <p style="color: #4b5563; font-size: 14px 16px; margin-bottom: 16px;">{{ album.description || '暂无描述' }}</p>
            <div style="display: flex; flex-wrap: justify-content: center; gap: 8px 16px; @media (min-width: 640px) { justify-content: flex-start; }">
              <span style="display: inline-block; padding: 4px 12px; font-size: 12px 14px; font-weight: 500; border-radius: 9999px; background-color: #dbeafe; color: #1e40af;">
                {{ episodes.length }} 个音频
              </span>
              <span style="display: inline-block; padding: 4px 12px; font-size: 12px 14px; font-weight: 500; border-radius: 9999px; background-color: #f3f4f6; color: #374151;">
                创建于 {{ formatDate(album.created_at) }}
              </span>
            </div>

            <div style="margin-top: 16px 24px; display: flex; justify-content: center; @media (min-width: 640px) { justify-content: flex-start; }">
              <button
                @click="showEditModal = true"
                style="background-color: #dbeafe; color: #1e40af; padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#bfdbfe'"
                onmouseout="this.style.backgroundColor='#dbeafe'"
              >
                编辑专辑
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 单集列表头部 -->
      <div v-if="album" style="margin-bottom: 16px; display: flex; flex-direction: column; gap: 12px; @media (min-width: 640px) { flex-direction: row; justify-content: space-between; align-items: center; }">
        <h2 style="font-size: 18px 20px; font-weight: bold; color: #1f2937;">
          🎧 单集列表 ({{ episodes.length }})
        </h2>
        <div v-if="isAdmin" style="display: flex; gap: 8px;">
          <button
            v-if="episodes.length > 0"
            @click="showSearchBox = !showSearchBox"
            style="background-color: #10b981; color: white; padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
            onmouseover="this.style.backgroundColor='#059669'"
            onmouseout="this.style.backgroundColor='#10b981'"
          >
            🔍<span style="display: none; @media (min-width: 640px) { display: inline; margin-left: 4px; }">搜索</span>
          </button>
          <button
            @click="showCreateEpisodeModal = true"
            style="background-color: #10b981; color: white; padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
            onmouseover="this.style.backgroundColor='#059669'"
            onmouseout="this.style.backgroundColor='#10b981'"
          >
            <span style="margin-right: 4px;">＋</span>
            <span style="display: none; @media (min-width: 640px) { display: inline; }">新建单集</span>
          </button>
          <button
            @click="triggerBatchUpload"
            style="background-color: #16a34a; color: white; padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
            onmouseover="this.style.backgroundColor='#15803d'"
            onmouseout="this.style.backgroundColor='#16a34a'"
          >
            📤<span style="display: none; @media (min-width: 640px) { display: inline; margin-left: 4px; }">批量上传</span>
          </button>
          <input
            ref="batchUploadInput"
            type="file"
            multiple
            accept="audio/*"
            @change="handleBatchUpload"
            style="display: none"
          />
        </div>
      </div>

      <!-- 上传进度显示 -->
      <div v-if="showProgress" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 14px; font-weight: 500; color: #1f2937;">
            📤 {{ uploadStatus || '上传中...' }}
          </span>
          <span style="font-size: 14px; font-weight: bold; color: #10b981;">
            {{ uploadProgress }}%
          </span>
        </div>
        <div style="width: 100%; height: 8px; background-color: #f3f4f6; border-radius: 4px; overflow: hidden;">
          <div
            :style="{
              width: `${uploadProgress}%`,
              height: '100%',
              backgroundColor: '#10b981',
              transition: 'width 0.3s ease'
            }"
          ></div>
        </div>
      </div>

      <!-- 搜索框 -->
      <div v-if="showSearchBox" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px; margin-bottom: 16px;">
        <div style="display: flex; gap: 12px;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索单集标题..."
            style="flex: 1; padding: 10px 16px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; font-size: 14px;"
            onfocus="this.style.borderColor='#10b981'"
            onblur="this.style.borderColor='#d1d5db'"
            @keypress.enter="handleSearch"
          />
          <button
            @click="handleSearch"
            style="padding: 10px 20px; background-color: #10b981; color: white; font-weight: 500; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s; font-size: 14px;"
            onmouseover="this.style.backgroundColor='#059669'"
            onmouseout="this.style.backgroundColor='#10b981'"
          >
            搜索
          </button>
          <button
            v-if="searchQuery"
            @click="clearSearch"
            style="padding: 10px 20px; background-color: #9ca3af; color: white; font-weight: 500; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s; font-size: 14px;"
            onmouseover="this.style.backgroundColor='#6b7280'"
            onmouseout="this.style.backgroundColor='#9ca3af'"
          >
            清除
          </button>
        </div>
        <p v-if="searching" style="color: #6b7280; font-size: 12px; margin-top: 8px;">正在搜索...</p>
        <p v-else-if="searched && filteredEpisodes.length === 0 && episodes.length > 0" style="color: #ef4444; font-size: 12px; margin-top: 8px;">未找到匹配的单集</p>
        <p v-else-if="searched && filteredEpisodes.length > 0" style="color: #10b981; font-size: 12px; margin-top: 8px;">找到 {{ filteredEpisodes.length }} 个匹配的单集</p>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && episodes.length === 0" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 32px 48px; text-align: center;">
        <div style="font-size: 48px 64px; margin-bottom: 16px;">🎧</div>
        <h3 style="font-size: 18px 20px; font-weight: 600; color: #374151; margin-bottom: 8px;">暂无音频</h3>
        <p style="color: #6b7280; font-size: 14px 16px;">点击上方按钮添加你的第一个音频</p>
      </div>

      <!-- 单集列表 - 简化布局（只显示文件名、时长和操作） -->
      <div v-else style="display: flex; flex-direction: column; gap: 8px;">
        <div
          v-for="episode in filteredEpisodes"
          :key="episode.id"
          style="display: flex; align-items: center; background-color: white; border-radius: 8px; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); padding: 12px 16px; transition: box-shadow 0.2s;"
          onmouseover="this.style.boxShadow='0 2px 4px -1px rgba(0, 0, 0, 0.1)'"
          onmouseout="this.style.boxShadow='0 1px 2px 0 rgba(0, 0, 0, 0.05)'"
        >
          <!-- 文件名和时长 -->
          <div
            @click="navigateTo(`/player/${episode.id}`)"
            style="flex: 1; min-width: 0; cursor: pointer; display: flex; flex-direction: column; gap: 4px;"
          >
            <div
              style="font-weight: 500; font-size: 14px 15px; color: #1f2937; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
            >
              {{ episode.title }}
            </div>
            <div style="font-size: 12px 13px; color: #6b7280;">
              ⏱️ {{ formatDuration(episode.duration) }}
            </div>
          </div>

          <!-- 操作按钮 -->
          <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
            <!-- 播放按钮 -->
            <button
              @click="navigateTo(`/player/${episode.id}`)"
              style="width: 32px 36px; height: 32px 36px; background-color: #10b981; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer; font-size: 14px; transition: background-color 0.2s;"
              onmouseover="this.style.backgroundColor='#059669'"
              onmouseout="this.style.backgroundColor='#10b981'"
            >
              ▶️
            </button>

            <!-- 编辑和删除按钮（仅管理员） -->
            <div v-if="isAdmin" style="display: flex; gap: 4px;">
              <button
                @click="handleEditEpisode(episode)"
                style="width: 32px 36px; height: 32px 36px; background-color: #10b981; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer; font-size: 12px; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#059669'"
                onmouseout="this.style.backgroundColor='#10b981'"
              >
                ✏️
              </button>
              <button
                @click="handleDeleteEpisode(episode.id)"
                style="width: 32px 36px; height: 32px 36px; background-color: #dc2626; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer; font-size: 12px; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#b91c1c'"
                onmouseout="this.style.backgroundColor='#dc2626'"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑专辑弹窗 -->
    <div v-if="showEditModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">编辑专辑</h2>

          <form @submit.prevent="handleEditAlbum">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">标题</label>
              <input
                v-model="editForm.title"
                type="text"
                placeholder="请输入专辑标题"
                required
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="margin-bottom: 24px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">描述</label>
              <textarea
                v-model="editForm.description"
                placeholder="请输入专辑描述（可选）"
                rows="3"
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s; resize: none;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              ></textarea>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button
                type="button"
                @click="showEditModal = false"
                style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#f9fafb'"
                onmouseout="this.style.backgroundColor='white'"
              >
                取消
              </button>
              <button
                type="submit"
                style="padding: 8px 16px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; border: none;"
                onmouseover="this.style.backgroundColor='#059669'"
                onmouseout="this.style.backgroundColor='#10b981'"
              >
                保存
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 创建单集弹窗 -->
    <div v-if="showCreateEpisodeModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">新建单集</h2>

          <form @submit.prevent="handleCreateEpisode">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">标题</label>
              <input
                v-model="newEpisode.title"
                type="text"
                placeholder="请输入单集标题"
                required
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="margin-bottom: 24px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">音频文件</label>
              <input
                ref="audioFileInput"
                type="file"
                accept="audio/*"
                required
                style="width: 100%; font-size: 14px; color: #6b7280;"
              />
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button
                type="button"
                @click="showCreateEpisodeModal = false"
                style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#f9fafb'"
                onmouseout="this.style.backgroundColor='white'"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="uploading"
                style="padding: 8px 16px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; border: none;"
                onmouseover="!this.disabled && (this.style.backgroundColor='#059669')"
                onmouseout="!this.disabled && (this.style.backgroundColor='#10b981')"
              >
                {{ uploading ? '上传中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑单集弹窗 -->
    <div v-if="showEditEpisodeModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">编辑单集</h2>

          <form @submit.prevent="handleUpdateEpisode">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">标题</label>
              <input
                v-model="editingEpisode.title"
                type="text"
                placeholder="请输入单集标题"
                required
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button
                type="button"
                @click="showEditEpisodeModal = false"
                style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#f9fafb'"
                onmouseout="this.style.backgroundColor='white'"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="updating"
                style="padding: 8px 16px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; border: none;"
                onmouseover="!this.disabled && (this.style.backgroundColor='#059669')"
                onmouseout="!this.disabled && (this.style.backgroundColor='#10b981')"
              >
                {{ updating ? '更新中...' : '更新' }}
              </button>
            </div>
          </form>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const route = useRoute()
const { $albumApi, $episodeApi } = useNuxtApp()

// 从 localStorage 获取用户信息
const user = computed(() => {
  if (import.meta.client) {
    const userData = localStorage.getItem('user')
    return userData ? JSON.parse(userData) : null
  }
  return null
})

const getUserDisplayName = () => {
  return user.value?.first_name && user.value?.last_name
    ? `${user.value.first_name} ${user.value.last_name}`
    : user.value?.username || '未知用户'
}

// 检查用户是否是管理员
const isAdmin = computed(() => {
  return user.value?.role === 'admin'
})

const albumId = ref<number>(parseInt(route.params.id as string))

const album = ref<any>(null)
const episodes = ref<any[]>([])
const filteredEpisodes = ref<any[]>([])
const loading = ref(true)
const uploading = ref(false)
const updating = ref(false)

// 自定义 Toast 状态
const toast = ref({
  show: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'warning'
})

const showEditModal = ref(false)
const editForm = ref({ title: '', description: '' })

const showEditEpisodeModal = ref(false)
const showSearchBox = ref(false)
const searchQuery = ref('')
const searching = ref(false)
const searched = ref(false)
const editingEpisode = ref({
  id: 0,
  title: '',
  sort_order: 0
})

const showCreateEpisodeModal = ref(false)
const newEpisode = ref({ title: '' })
const audioFileInput = ref<HTMLInputElement | null>(null)
const batchUploadInput = ref<HTMLInputElement | null>(null)

// 上传进度相关
const uploadProgress = ref(0)
const showProgress = ref(false)
const uploadStatus = ref('')

// 显示 Toast 提示
const showToast = (message: string, type: 'success' | 'error' | 'warning' = 'info') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const loadAlbum = async () => {
  try {
    const response = await $albumApi.get(albumId.value)
    album.value = response.data
    editForm.value = { title: response.data.title, description: response.data.description || '' }
  } catch (error) {
    showToast('加载专辑失败', 'error')
  }
}

const loadEpisodes = async () => {
  try {
    // 只请求必要的字段，减少数据传输量
    const response = await $episodeApi.getByAlbum(albumId.value, 'id,title,duration')
    episodes.value = response.data.items
    filteredEpisodes.value = response.data.items
  } catch (error) {
    showToast('加载单集失败', 'error')
  } finally {
    loading.value = false
  }
}

const handleEditAlbum = async () => {
  try {
    await $albumApi.update(albumId.value, {
      title: editForm.value.title,
      description: editForm.value.description
    })
    showToast('专辑更新成功', 'success')
    showEditModal.value = false
    await loadAlbum()
  } catch (error) {
    showToast('更新专辑失败', 'error')
  }
}

const handleCreateEpisode = async () => {
  const file = audioFileInput.value?.files?.[0]
  if (!file) {
    showToast('请选择音频文件', 'warning')
    return
  }

  if (!newEpisode.value.title.trim()) {
    showToast('请输入单集标题', 'warning')
    return
  }

  uploading.value = true
  showProgress.value = true
  uploadProgress.value = 0
  uploadStatus.value = `正在上传: ${file.name}`

  try {
    const createResponse = await $episodeApi.create(albumId.value, {
      title: newEpisode.value.title,
      sort_order: episodes.value.length
    })
    const newId = createResponse.data.id

    await $episodeApi.upload(newId, file, (progress) => {
      uploadProgress.value = progress
    })

    showToast('单集创建成功', 'success')
    showCreateEpisodeModal.value = false
    newEpisode.value = { title: '' }
    await loadEpisodes()
  } catch (error) {
    showToast('创建单集失败', 'error')
  } finally {
    uploading.value = false
    showProgress.value = false
    uploadProgress.value = 0
  }
}

const triggerBatchUpload = () => {
  batchUploadInput.value?.click()
}

const handleBatchUpload = async () => {
  const files = batchUploadInput.value?.files
  if (!files || files.length === 0) return

  uploading.value = true
  showProgress.value = true
  uploadProgress.value = 0
  uploadStatus.value = `正在上传 ${files.length} 个文件...`

  try {
    await $episodeApi.batchUpload(albumId.value, Array.from(files), (progress) => {
      uploadProgress.value = progress
    })

    showToast(`成功上传 ${files.length} 个文件`, 'success')
    await loadEpisodes()
  } catch (error) {
    showToast('批量上传失败', 'error')
  } finally {
    uploading.value = false
    showProgress.value = false
    uploadProgress.value = 0
    if (batchUploadInput.value) {
      batchUploadInput.value.value = ''
    }
  }
}

const handleDeleteEpisode = async (episodeId: number) => {
  // 权限检查
  if (!isAdmin.value) {
    showToast('没有删除权限，请使用管理员账号登录', 'error')
    return
  }

  if (confirm('确定要删除这个音频吗？')) {
    try {
      console.log('删除剧集，ID:', episodeId)
      const response = await $episodeApi.delete(episodeId)
      console.log('删除响应:', response)
      showToast('删除成功', 'success')
      await loadEpisodes()
      // 重新过滤搜索结果
      if (searchQuery.value.trim()) {
        handleSearch()
      }
    } catch (error: any) {
      console.error('删除失败:', error)
      const errorMessage = error.response?.data?.detail || error.message || '删除失败'
      showToast(errorMessage, 'error')
    }
  }
}

const handleEditEpisode = (episode: any) => {
  // 权限检查
  if (!isAdmin.value) {
    showToast('没有编辑权限，请使用管理员账号登录', 'error')
    return
  }
  editingEpisode.value = { ...episode }
  showEditEpisodeModal.value = true
}

const handleUpdateEpisode = async () => {
  if (!editingEpisode.value.title.trim()) {
    showToast('请输入单集标题', 'warning')
    return
  }

  updating.value = true
  try {
    await $episodeApi.update(editingEpisode.value.id, {
      title: editingEpisode.value.title,
      sort_order: editingEpisode.value.sort_order
    })
    showToast('单集更新成功', 'success')
    showEditEpisodeModal.value = false
    editingEpisode.value = { id: 0, title: '', sort_order: 0 }
    await loadEpisodes()
    // 重新过滤搜索结果
    if (searchQuery.value.trim()) {
      handleSearch()
    }
  } catch (error) {
    showToast('更新单集失败', 'error')
  } finally {
    updating.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    showToast('请输入搜索关键词', 'warning')
    return
  }

  searching.value = true
  searched.value = true

  try {
    // 前端过滤
    const query = searchQuery.value.toLowerCase()
    filteredEpisodes.value = episodes.value.filter(episode =>
      episode.title?.toLowerCase().includes(query)
    )
    showToast(`找到 ${filteredEpisodes.value.length} 个匹配的单集`, 'success')
  } catch (error) {
    showToast('搜索失败', 'error')
  } finally {
    searching.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searched.value = false
  filteredEpisodes.value = [...episodes.value]
  showSearchBox.value = false
}

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatShortDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  loadAlbum()
  loadEpisodes()
})
</script>

<style scoped>
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>

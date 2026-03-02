<template>
  <div style="min-height: 100vh; background: linear-gradient(to bottom right, #eff6ff, #f3e8ff); padding-bottom: 48px;">
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

    <!-- 移动端优化的用户头部 -->
    <div style="background-color: white; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); border-bottom: 1px solid #e5e7eb; padding: 12px 16px; position: sticky; top: 0; z-index: 50;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 8px 12px;">
          <div style="width: 32px; height: 32px; background: linear-gradient(to bottom right, #10b981, #059669); border-radius: 9999px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">
            {{ user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div style="min-width: 0;">
            <div style="display: flex; align-items: center; gap: 4px 8px;">
              <span style="font-weight: 600; color: #1f2937; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {{ getUserDisplayName() }}
              </span>
              <span
                v-if="isAdmin()"
                style="display: inline-block; padding: 2px 8px; font-size: 12px; font-weight: 500; border-radius: 9999px; background-color: #fee2e2; color: #991b1b;"
              >
                管理员
              </span>
            </div>
            <div style="font-size: 12px; color: #6b7280;">
              {{ user?.is_active ? '在线' : '离线' }} · ID: {{ user?.id }}
            </div>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 8px;">
          <button
            v-if="user"
            @click="showChangePasswordModal = true"
            style="background-color: #3b82f6; color: white; padding: 6px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
            onmouseover="this.style.backgroundColor='#2563eb'"
            onmouseout="this.style.backgroundColor='#3b82f6'"
          >
            修改密码
          </button>
          <button
            @click="handleLogout"
            style="background-color: #fee2e2; color: #b91c1c; padding: 6px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
            onmouseover="this.style.backgroundColor='#fecaca'"
            onmouseout="this.style.backgroundColor='#fee2e2'"
          >
            退出登录
          </button>
        </div>
      </div>
    </div>

    <div style="max-width: 80rem; margin: 0 auto; padding: 12px 12px 16px;">
      <!-- 页面标题和操作 -->
      <div class="page-header">
        <div>
          <h1 class="page-title">📚 我的专辑</h1>
          <p class="page-subtitle">管理你的广播剧专辑和音频内容</p>
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <button
            v-if="isAdmin()"
            @click="navigateTo('/users')"
            style="background-color: #f59e0b; color: white; font-weight: 500; padding: 10px 16px; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s; font-size: 14px;"
            onmouseover="this.style.backgroundColor='#d97706'"
            onmouseout="this.style.backgroundColor='#f59e0b'"
          >
            👥 用户管理
          </button>
          <button
            v-if="isAdmin() && albums.length > 0"
            @click="showSearchBox = !showSearchBox"
            style="background-color: #10b981; color: white; font-weight: 500; padding: 10px 16px; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s; font-size: 14px;"
            onmouseover="this.style.backgroundColor='#059669'"
            onmouseout="this.style.backgroundColor='#10b981'"
          >
            🔍 搜索
          </button>
          <button
            v-if="isAdmin()"
            @click="showCreateModal = true"
            style="background-color: #10b981; color: white; font-weight: 500; padding: 10px 16px; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s; font-size: 14px;"
            onmouseover="this.style.backgroundColor='#059669'"
            onmouseout="this.style.backgroundColor='#10b981'"
          >
            <span style="font-size: 18px; margin-right: 4px;">＋</span>
            新建专辑
          </button>
        </div>
      </div>

      <!-- 搜索框 -->
      <div v-if="showSearchBox" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px; margin-bottom: 24px;">
        <div style="display: flex; gap: 12px;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索专辑标题或描述..."
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
        <p v-else-if="searched && filteredAlbums.length === 0 && albums.length > 0" style="color: #ef4444; font-size: 12px; margin-top: 8px;">未找到匹配的专辑</p>
        <p v-else-if="searched && filteredAlbums.length > 0" style="color: #10b981; font-size: 12px; margin-top: 8px;">找到 {{ filteredAlbums.length }} 个匹配的专辑</p>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && albums.length === 0" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 32px 48px; text-align: center;">
        <div style="font-size: 48px 64px; margin-bottom: 16px;">📭</div>
        <h3 style="font-size: 18px 20px; font-weight: 600; color: #374151; margin-bottom: 8px;">暂无专辑</h3>
        <p style="color: #6b7280; font-size: 14px 16px; margin-bottom: 24px;">点击"新建专辑"按钮创建你的第一个专辑</p>
      </div>

      <!-- 加载状态 - 骨架屏（无封面，仅信息块） -->
      <div v-else-if="loading" class="album-grid">
        <!-- 骨架屏卡片 x6 -->
        <div
          v-for="i in 6"
          :key="'skeleton-' + i"
          style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); overflow: hidden; padding: 16px 20px;"
        >
          <div
            :style="{
              height: '20px',
              background: 'linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s infinite',
              borderRadius: '4px',
              marginBottom: '8px',
              maxWidth: '70%'
            }"
          ></div>
          <div
            :style="{
              height: '16px',
              background: 'linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s infinite',
              borderRadius: '4px',
              marginBottom: '6px',
              maxWidth: '90%'
            }"
          ></div>
          <div
            :style="{
              height: '14px',
              background: 'linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s infinite',
              borderRadius: '4px',
              maxWidth: '50%'
            }"
          ></div>
        </div>
      </div>

      <!-- 专辑列表 - 响应式网格（管理员左滑显示删除按钮） -->
      <div v-else class="album-grid">
        <div
          v-for="album in filteredAlbums"
          :key="album.id"
          style="display: flex; position: relative; overflow: hidden; border-radius: 12px;"
        >
          <!-- 专辑卡片内容（无封面，仅信息块） -->
          <div
            @click="navigateTo(`/albums/${album.id}`)"
            style="flex: 1; background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); overflow: hidden; cursor: pointer; transition: box-shadow 0.2s; position: relative; z-index: 10;"
            onmouseover="this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)'"
            onmouseout="this.style.boxShadow='0 1px 3px 0 rgba(0, 0, 0, 0.1)'"
          >
            <!-- 专辑信息 -->
            <div style="padding: 16px 20px;">
              <h2 class="album-title">
                {{ album.title }}
              </h2>
              <p class="album-desc">
                {{ album.description || '暂无描述' }}
              </p>
              <div style="display: flex; align-items: center; font-size: 12px; color: #9ca3af;">
                <span>📅 {{ formatDate(album.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 按钮区域（右侧） -->
          <div v-if="isAdmin()" style="flex-shrink: 0; width: 76px; display: flex; z-index: 20; position: absolute; right: 0; top: 0; bottom: 0;">
            <div
              @click.stop="handleEdit(album)"
              style="flex: 1; background-color: #10b981; color: white; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
              onmouseover="this.style.backgroundColor='#059669'"
              onmouseout="this.style.backgroundColor='#10b981'"
            >
              ✏️
            </div>
            <div
              @click.stop="handleDelete(album)"
              style="flex: 1; background-color: #dc2626; color: white; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
              onmouseover="this.style.backgroundColor='#b91c1c'"
              onmouseout="this.style.backgroundColor='#dc2626'"
            >
              🗑️
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建专辑弹窗 -->
    <div v-if="showCreateModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">新建专辑</h2>

          <form @submit.prevent="handleCreate">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">标题</label>
              <input
                v-model="newAlbum.title"
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
                v-model="newAlbum.description"
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
                @click="showCreateModal = false"
                style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#f9fafb'"
                onmouseout="this.style.backgroundColor='white'"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="creating"
                style="padding: 8px 16px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; border: none;"
                onmouseover="!this.disabled && (this.style.backgroundColor='#059669')"
                onmouseout="!this.disabled && (this.style.backgroundColor='#10b981')"
              >
                {{ creating ? '创建中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑专辑弹窗 -->
    <div v-if="showEditModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">编辑专辑</h2>

          <form @submit.prevent="handleUpdate">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">标题</label>
              <input
                v-model="editingAlbum.title"
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
                v-model="editingAlbum.description"
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

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePasswordModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">修改密码</h2>

          <form @submit.prevent="handleChangePassword">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">原密码</label>
              <input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入原密码"
                required
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">新密码</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码（至少6个字符）"
                required
                minlength="6"
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="margin-bottom: 24px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认新密码</label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                required
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button
                type="button"
                @click="showChangePasswordModal = false"
                style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer; transition: background-color 0.2s;"
                onmouseover="this.style.backgroundColor='#f9fafb'"
                onmouseout="this.style.backgroundColor='white'"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="changingPassword"
                style="padding: 8px 16px; background-color: #3b82f6; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; border: none;"
                onmouseover="!this.disabled && (this.style.backgroundColor='#2563eb')"
                onmouseout="!this.disabled && (this.style.backgroundColor='#3b82f6'"
              >
                {{ changingPassword ? '修改中...' : '确认修改' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const { $albumApi, $authApi } = useNuxtApp()

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

const isAdmin = () => {
  return user.value?.role === 'admin'
}

const albums = ref<any[]>([])
const filteredAlbums = ref<any[]>([])
const loading = ref(true)
const creating = ref(false)
const updating = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showSearchBox = ref(false)
const newAlbum = ref({ title: '', description: '', cover_image: '' })
const editingAlbum = ref({ id: 0, title: '', description: '', cover_image: '' })
const searchQuery = ref('')
const searching = ref(false)
const searched = ref(false)

// 修改密码相关
const showChangePasswordModal = ref(false)
const changingPassword = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 自定义 Toast 状态
const toast = ref({
  show: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'warning'
})

// 显示 Toast 提示
const showToast = (message: string, type: 'success' | 'error' | 'warning' = 'info') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const loadAlbums = async () => {
  loading.value = true
  try {
    const response = await $albumApi.list()
    albums.value = response.data.items
    filteredAlbums.value = response.data.items
  } catch (error) {
    showToast('加载专辑失败', 'error')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!newAlbum.value.title.trim()) {
    showToast('请输入专辑标题', 'warning')
    return
  }

  creating.value = true
  try {
    await $albumApi.create({
      title: newAlbum.value.title,
      description: newAlbum.value.description
    })
    showToast('专辑创建成功', 'success')
    showCreateModal.value = false
    newAlbum.value = { title: '', description: '', cover_image: '' }
    await loadAlbums()
  } catch (error) {
    showToast('创建专辑失败', 'error')
  } finally {
    creating.value = false
  }
}

const handleEdit = (album: any) => {
  editingAlbum.value = { ...album }
  showEditModal.value = true
}

const handleUpdate = async () => {
  if (!editingAlbum.value.title.trim()) {
    showToast('请输入专辑标题', 'warning')
    return
  }

  updating.value = true
  try {
    await $albumApi.update(editingAlbum.value.id, {
      title: editingAlbum.value.title,
      description: editingAlbum.value.description || undefined,
      cover_image: editingAlbum.value.cover_image || '/default-cover.svg'
    })
    showToast('专辑更新成功', 'success')
    showEditModal.value = false
    editingAlbum.value = { id: 0, title: '', description: '', cover_image: '' }
    await loadAlbums()
  } catch (error) {
    showToast('更新专辑失败', 'error')
  } finally {
    updating.value = false
  }
}

const handleDelete = async (album: any) => {
  if (confirm(`确定要删除专辑"${album.title}"吗？删除后无法恢复！`)) {
    try {
      await $albumApi.delete(album.id)
      showToast('专辑删除成功', 'success')
      await loadAlbums()
    } catch (error) {
      showToast('删除专辑失败', 'error')
    }
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
    // 前端过滤（如果后端没有搜索接口）
    const query = searchQuery.value.toLowerCase()
    filteredAlbums.value = albums.value.filter(album => 
      album.title?.toLowerCase().includes(query) ||
      album.description?.toLowerCase().includes(query)
    )
    showToast(`找到 ${filteredAlbums.value.length} 个匹配的专辑`, 'success')
  } catch (error) {
    showToast('搜索失败', 'error')
  } finally {
    searching.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searched.value = false
  filteredAlbums.value = [...albums.value]
  showSearchBox.value = false
}

const handleChangePassword = async () => {
  if (!passwordForm.value.oldPassword.trim()) {
    showToast('请输入原密码', 'warning')
    return
  }
  if (!passwordForm.value.newPassword.trim()) {
    showToast('请输入新密码', 'warning')
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    showToast('新密码至少需要6个字符', 'warning')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showToast('两次输入的新密码不一致', 'warning')
    return
  }

  changingPassword.value = true
  try {
    // 验证原密码是否正确
    await $authApi.login({
      username: user.value?.username || '',
      password: passwordForm.value.oldPassword
    })

    // 更新密码
    await $authApi.updateUser(user.value?.id || 0, {
      password: passwordForm.value.newPassword
    })

    showToast('密码修改成功，请重新登录', 'success')
    showChangePasswordModal.value = false
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }

    // 重新登录
    setTimeout(() => {
      handleLogout()
    }, 1500)
  } catch (error: any) {
    const message = error.response?.data?.detail || '密码修改失败，请检查原密码是否正确'
    showToast(message, 'error')
  } finally {
    changingPassword.value = false
  }
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    try {
      if (import.meta.client) {
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    } catch (error) {
      // Ignore logout error
    }
    await navigateTo('/login')
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  // 未登录用户直接跳转到登录页
  if (!user.value) {
    navigateTo('/login')
    return
  }

  loadAlbums()
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

/* 页面标题区域：默认针对手机优化 */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.page-subtitle {
  color: #4b5563;
  font-size: 13px;
}

/* 专辑网格：默认单列，手机更易点击 */
.album-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 12px 16px;
}

.album-title {
  font-weight: 700;
  font-size: 15px;
  color: #1f2937;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-desc {
  color: #6b7280;
  font-size: 12px;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 大屏时再增强布局 */
@media (min-width: 640px) {
  .page-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .page-title {
    font-size: 24px;
    margin-bottom: 8px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .album-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px 20px;
  }
}

@media (min-width: 1024px) {
  .album-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>

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
          <div style="width: 32px; height: 32px; background: linear-gradient(to bottom right, #3b82f6, #a855f7); border-radius: 9999px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">
            {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div style="min-width: 0;">
            <div style="display: flex; align-items: center; gap: 4px 8px;">
              <span style="font-weight: 600; color: #1f2937; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {{ authStore.getUserDisplayName() }}
              </span>
              <span
                v-if="authStore.isAdmin()"
                style="display: inline-block; padding: 2px 8px; font-size: 12px; font-weight: 500; border-radius: 9999px; background-color: #fee2e2; color: #991b1b;"
              >
                管理员
              </span>
            </div>
            <div style="font-size: 12px; color: #6b7280;">
              {{ authStore.user?.is_active ? '在线' : '离线' }} · ID: {{ authStore.user?.id }}
            </div>
          </div>
        </div>

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

    <div style="max-width: 80rem; margin: 0 auto; padding: 16px 24px;">
      <!-- 页面标题和操作 -->
      <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px 32px; @media (min-width: 640px) { flex-direction: row; justify-content: space-between; align-items: center; }">
        <div>
          <h1 style="font-size: 24px 28px; font-weight: bold; color: #1f2937; margin-bottom: 8px;">📚 我的专辑</h1>
          <p style="color: #4b5563; font-size: 14px 16px;">管理你的广播剧专辑和音频内容</p>
        </div>
        <button
          @click="showCreateModal = true"
          style="background-color: #2563eb; color: white; font-weight: 500; padding: 10px 16px; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s; font-size: 14px;"
          onmouseover="this.style.backgroundColor='#1d4ed8'"
          onmouseout="this.style.backgroundColor='#2563eb'"
        >
          <span style="font-size: 18px; margin-right: 4px;">＋</span>
          新建专辑
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && albums.length === 0" style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 32px 48px; text-align: center;">
        <div style="font-size: 48px 64px; margin-bottom: 16px;">📭</div>
        <h3 style="font-size: 18px 20px; font-weight: 600; color: #374151; margin-bottom: 8px;">暂无专辑</h3>
        <p style="color: #6b7280; font-size: 14px 16px; margin-bottom: 24px;">点击"新建专辑"按钮创建你的第一个专辑</p>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="loading" style="display: flex; justify-content: center; padding: 48px;">
        <div style="color: #3b82f6; font-size: 14px;">加载中...</div>
      </div>

      <!-- 专辑列表 - 响应式网格 -->
      <div v-else style="display: grid; grid-template-columns: repeat(1, minmax(0, 1fr)); gap: 16px 24px; @media (min-width: 640px) { grid-template-columns: repeat(2, minmax(0, 1fr)); } @media (min-width: 1024px) { grid-template-columns: repeat(3, minmax(0, 1fr)); }">
        <div
          v-for="album in albums"
          :key="album.id"
          @click="$router.push(`/albums/${album.id}`)"
          style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); overflow: hidden; cursor: pointer; transition: all 0.2s;"
        >
          <!-- 封面图 -->
          <div style="height: 160px 192px; position: relative; overflow: hidden; background: linear-gradient(to bottom right, #818cf8, #a855f7);">
            <div
              v-if="album.cover_image"
              :style="{
                width: '100%',
                height: '100%',
                backgroundImage: `url(${album.cover_image})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }"
            ></div>
            <div v-else style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
              <span style="color: white; font-size: 48px 64px; opacity: 0.8;">📚</span>
            </div>
            <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.5), transparent); padding: 12px 16px;">
              <span style="color: white; font-size: 12px 14px; font-weight: 500;">{{ album.episode_count }} 个音频</span>
            </div>
          </div>

          <!-- 专辑信息 -->
          <div style="padding: 16px 20px;">
            <h2 style="font-weight: bold; font-size: 16px 18px; color: #1f2937; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              {{ album.title }}
            </h2>
            <p style="color: #6b7280; font-size: 12px 14px; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
              {{ album.description || '暂无描述' }}
            </p>
            <div style="display: flex; align-items: center; font-size: 12px; color: #9ca3af;">
              <span>{{ formatDate(album.created_at) }}</span>
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
                onfocus="this.style.borderColor='#3b82f6'"
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
                onfocus="this.style.borderColor='#3b82f6'"
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
                style="padding: 8px 16px; background-color: #2563eb; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; border: none;"
                onmouseover="!this.disabled && (this.style.backgroundColor='#1d4ed8')"
                onmouseout="!this.disabled && (this.style.backgroundColor='#2563eb')"
              >
                {{ creating ? '创建中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { albumApi, DEFAULT_COVER } from '@/api/album'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const albums = ref<any[]>([])
const loading = ref(true)
const creating = ref(false)
const showCreateModal = ref(false)
const newAlbum = ref({ title: '', description: '', cover_image: DEFAULT_COVER })

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
    const response = await albumApi.list()
    albums.value = response.data.items
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
    await albumApi.create({
      title: newAlbum.value.title,
      description: newAlbum.value.description || undefined,
      cover_image: DEFAULT_COVER
    })
    showToast('专辑创建成功', 'success')
    showCreateModal.value = false
    newAlbum.value = { title: '', description: '', cover_image: DEFAULT_COVER }
    await loadAlbums()
  } catch (error) {
    showToast('创建专辑失败', 'error')
  } finally {
    creating.value = false
  }
}

const handleLogout = async () => {
  if (confirm('确定要退出登录吗？')) {
    try {
      await authStore.logout()
    } catch (error) {
      // Ignore logout error
    }
    router.push('/login')
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
</style>

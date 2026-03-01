<template>
  <div style="min-height: 100vh; background: linear-gradient(135deg, #f0fdf4, #dcfce7, #bbf7d0);">
    <!-- 头部 -->
    <div style="background-color: white; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px 20px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-size: 24px; font-weight: bold; color: #166534; margin: 0;">用户管理</h1>
        <p style="color: #6b7280; font-size: 14px; margin: 4px 0 0 0;">管理系统用户</p>
      </div>

      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 32px; height: 32px; background: linear-gradient(to bottom right, #10b981, #059669); border-radius: 9999px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">
            {{ user?.username.charAt(0).toUpperCase() }}
          </div>
          <span style="color: #374151; font-size: 14px;">{{ getUserDisplayName() }}</span>
        </div>
        <button
          @click="navigateTo('/')"
          style="padding: 8px 16px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
          onmouseover="this.style.backgroundColor='#059669'"
          onmouseout="this.style.backgroundColor='#10b981'"
        >
          返回专辑列表
        </button>
        <button
          @click="handleLogout"
          style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer;"
        >
          退出登录
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div style="max-width: 1408px; margin: 0 auto; padding: 24px 16px;">
      <!-- 操作栏 -->
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 16px 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 16px;">
          <h2 style="font-size: 18px; font-weight: bold; color: #166534; margin: 0;">用户列表</h2>
          <span style="color: #6b7280; font-size: 14px;">共 {{ users.length }} 个用户</span>
        </div>
        <button
          @click="showCreateModal = true"
          style="padding: 10px 20px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s;"
          onmouseover="this.style.backgroundColor='#059669'"
          onmouseout="this.style.backgroundColor='#10b981'"
        >
          新建用户
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" style="display: flex; justify-content: center; padding: 48px;">
        <div style="color: #10b981; font-size: 14px;">加载中...</div>
      </div>

      <!-- 用户列表 -->
      <div v-else style="background-color: white; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); overflow: hidden;">
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="background-color: #f9fafb; border-bottom: 1px solid #e5e7eb;">
              <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #6b7280; font-size: 14px;">用户名</th>
              <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #6b7280; font-size: 14px;">角色</th>
              <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #6b7280; font-size: 14px;">状态</th>
              <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #6b7280; font-size: 14px;">创建时间</th>
              <th style="padding: 12px 16px; text-align: right; font-weight: 600; color: #6b7280; font-size: 14px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 12px 16px; font-size: 14px; color: #374151;">{{ user.username }}</td>
              <td style="padding: 12px 16px;">
                <span
                  :style="{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 500,
                    backgroundColor: user.role === 'admin' ? '#dcfce7' : '#f3f4f6',
                    color: user.role === 'admin' ? '#166534' : '#6b7280'
                  }"
                >
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td style="padding: 12px 16px;">
                <span
                  :style="{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 500,
                    backgroundColor: user.is_active ? '#dcfce7' : '#fef2f2',
                    color: user.is_active ? '#166534' : '#991b1b'
                  }"
                >
                  {{ user.is_active ? '激活' : '停用' }}
                </span>
              </td>
              <td style="padding: 12px 16px; font-size: 14px; color: #6b7280;">{{ formatDate(user.created_at) }}</td>
              <td style="padding: 12px 16px; text-align: right;">
                <button
                  @click="handleEdit(user)"
                  :disabled="user.id === currentUserId"
                  :style="{
                    padding: '6px 12px',
                    backgroundColor: '#10b981',
                    color: 'white',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 500,
                    border: 'none',
                    cursor: user.id !== currentUserId ? 'pointer' : 'not-allowed',
                    opacity: user.id === currentUserId ? 0.5 : 1,
                    marginRight: '8px'
                  }"
                >
                  编辑
                </button>
                <button
                  @click="handleDelete(user)"
                  :disabled="user.id === currentUserId"
                  :style="{
                    padding: '6px 12px',
                    backgroundColor: '#dc2626',
                    color: 'white',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 500,
                    border: 'none',
                    cursor: user.id !== currentUserId ? 'pointer' : 'not-allowed',
                    opacity: user.id === currentUserId ? 0.5 : 1
                  }"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="users.length === 0" style="padding: 48px; text-align: center;">
          <div style="font-size: 48px; margin-bottom: 16px;">👥</div>
          <h3 style="font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 8px;">暂无用户</h3>
          <p style="color: #6b7280; font-size: 14px; margin-bottom: 24px;">点击"新建用户"按钮创建第一个用户</p>
        </div>
      </div>
    </div>

    <!-- 创建/编辑用户弹窗 -->
    <div v-if="showCreateModal || showEditModal" style="position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px;">
      <div style="background-color: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); width: 100%; max-width: 448px;">
        <div style="padding: 16px 24px;">
          <h2 style="font-size: 20px 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px 24px;">
            {{ showCreateModal ? '新建用户' : '编辑用户' }}
          </h2>

          <form @submit.prevent="showCreateModal ? handleCreate() : handleUpdate()">
            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">用户名</label>
              <input
                v-model="editingUser.username"
                type="text"
                placeholder="请输入用户名"
                required
                :disabled="!!editingUser.id"
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="margin-bottom: 16px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">密码</label>
              <input
                v-model="editingUser.password"
                type="password"
                :placeholder="editingUser.id ? '留空则不修改密码' : '请输入密码'"
                :required="!editingUser.id"
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              />
            </div>

            <div style="margin-bottom: 24px;">
              <label style="display: block; color: #374151; font-size: 14px; font-weight: bold; margin-bottom: 8px;">角色</label>
              <select
                v-model="editingUser.role"
                style="width: 100%; padding: 8px 16px 12px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; transition: border-color 0.2s; background-color: white;"
                onfocus="this.style.borderColor='#10b981'"
                onblur="this.style.borderColor='#d1d5db'"
              >
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button
                type="button"
                @click="closeModal"
                style="padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background-color: white; color: #374151; font-weight: 500; cursor: pointer;"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="saving"
                style="padding: 8px 16px; background-color: #10b981; color: white; border-radius: 8px; font-weight: 500; cursor: pointer; border: none;"
              >
                {{ saving ? '保存中...' : (showCreateModal ? '创建' : '更新') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div v-if="toast.show" style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); padding: 12px 24px; border-radius: 8px; color: white; font-size: 14px; font-weight: 500; z-index: 100;" :style="{ backgroundColor: toast.type === 'success' ? '#10b981' : toast.type === 'error' ? '#dc2626' : '#f59e0b' }">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const { $authApi } = useNuxtApp()

// 用户信息
const user = computed(() => {
  if (import.meta.client) {
    const userData = localStorage.getItem('user')
    return userData ? JSON.parse(userData) : null
  }
  return null
})

const currentUserId = computed(() => user.value?.id || 0)

const getUserDisplayName = () => {
  return user.value?.username || '未知用户'
}

// 列表数据
const users = ref<any[]>([])
const loading = ref(true)

// 创建/编辑
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingUser = ref({ id: 0, username: '', password: '', role: 'user' })
const saving = ref(false)

// Toast 提示
const toast = ref({ show: false, message: '', type: 'success' as 'success' | 'error' | 'warning' })

const showToast = (message: string, type: 'success' | 'error' | 'warning' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await $authApi.getUsers()
    users.value = response.data.items
  } catch (error) {
    showToast('加载用户列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// 创建用户
const handleCreate = async () => {
  if (!editingUser.value.username.trim()) {
    showToast('请输入用户名', 'warning')
    return
  }
  if (!editingUser.value.password.trim()) {
    showToast('请输入密码', 'warning')
    return
  }

  saving.value = true
  try {
    await $authApi.createUser({
      username: editingUser.value.username,
      password: editingUser.value.password,
      role: editingUser.value.role
    })
    showToast('用户创建成功', 'success')
    closeModal()
    await loadUsers()
  } catch (error: any) {
    const message = error.response?.data?.detail || '创建用户失败'
    showToast(message, 'error')
  } finally {
    saving.value = false
  }
}

// 打开编辑弹窗
const handleEdit = (userData: any) => {
  editingUser.value = {
    id: userData.id,
    username: userData.username,
    password: '',
    role: userData.role
  }
  showEditModal.value = true
}

// 更新用户
const handleUpdate = async () => {
  if (!editingUser.value.username.trim()) {
    showToast('请输入用户名', 'warning')
    return
  }

  saving.value = true
  try {
    const updateData: any = {
      username: editingUser.value.username,
      role: editingUser.value.role
    }
    if (editingUser.value.password.trim()) {
      updateData.password = editingUser.value.password
    }
    await $authApi.updateUser(editingUser.value.id, updateData)
    showToast('用户更新成功', 'success')
    closeModal()
    await loadUsers()
  } catch (error: any) {
    const message = error.response?.data?.detail || '更新用户失败'
    showToast(message, 'error')
  } finally {
    saving.value = false
  }
}

// 删除用户
const handleDelete = async (userData: any) => {
  if (confirm(`确定要删除用户 "${userData.username}" 吗？删除后无法恢复！`)) {
    try {
      await $authApi.deleteUser(userData.id)
      showToast('用户删除成功', 'success')
      await loadUsers()
    } catch (error: any) {
      const message = error.response?.data?.detail || '删除用户失败'
      showToast(message, 'error')
    }
  }
}

// 关闭弹窗
const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingUser.value = { id: 0, username: '', password: '', role: 'user' }
}

// 退出登录
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

onMounted(() => {
  loadUsers()
})
</script>

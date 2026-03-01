export interface ApiClient {
  get<T = any>(url: string): Promise<{data: T}>
  post<T = any>(url: string, data?: any, config?: any): Promise<{data: T}>
  put<T = any>(url: string, data?: any): Promise<{data: T}>
  delete(url: string): Promise<any>
}

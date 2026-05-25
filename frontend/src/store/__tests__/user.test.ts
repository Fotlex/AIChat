import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from '../user';
import * as api from '@/api/userApi';

vi.mock('@/api/userApi', () => ({
  getUser: vi.fn(),
  getSettingsInfo: vi.fn()
}));

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('инициализируется с пустыми данными', () => {
    const store = useUserStore();
    expect(store.currentUser).toBeNull();
    expect(store.balance).toBe(0);
    expect(store.isLoading).toBe(false);
  });

  it('успешно загружает пользователя и обновляет баланс', async () => {
    const store = useUserStore();
    const mockUserData = { id: 1, username: 'fotlex', balance: 5000 };
    
    vi.mocked(api.getUser).mockResolvedValue(mockUserData);

    await store.fetchUser();

    expect(store.currentUser?.username).toBe('fotlex');
    expect(store.balance).toBe(5000);
    expect(store.isLoading).toBe(false);
  });
});
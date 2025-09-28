import apiClient from './apiClient';

export const getUser = async () => {
    const response = await apiClient.get('/users/current_user/');
    return response.data;
  };
<template>
  <button class="tariff-card" @click="onCardClick">
    <div v-if="isPopular" class="popular-badge">Популярное</div>

    <div class="tariff-card__content">
      <div v-if="tariff.photo" class="tariff-card__image-wrapper">
        <img :src="tariff.photo" :alt="tariff.name" class="tariff-card__image" />
      </div>
      <div class="tariff-card__reward">
        <span class="tariff-card__amount">{{ tariff.reward.toLocaleString('ru-RU') }}</span>
        <span class="tariff-card__currency">монет</span>
      </div>
    </div>

    <div class="tariff-card__footer">
      <span class="tariff-card__price">{{ tariff.cost.toLocaleString('ru-RU') }} ₽</span>
      <span class="tariff-card__arrow">→</span>
    </div>
  </button>
</template>

<script setup lang="ts">
import type { Tariff } from '@/types';


const props = defineProps<{
  tariff: Tariff;
  isPopular?: boolean;
}>();

const emit = defineEmits<{
  (e: 'select', tariff: Tariff): void;
}>();

function onCardClick() {
  emit('select', props.tariff);
}
</script>

<style scoped>
.tariff-card {
  position: relative; 
  overflow: hidden; 
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  padding: 16px;
  border-radius: 14px;
  border: 1px solid #3a3a3c;
  background-color: #2c2c2e;
  color: #fff;
  text-align: center;
  cursor: pointer;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.tariff-card:hover {
  transform: scale(1.03);
  border-color: #555;
  box-shadow: 0 0 20px rgba(0, 122, 255, 0.2);
}

.tariff-card:active {
  transform: scale(1.01);
}

.popular-badge {
  position: absolute;
  top: 12px;
  right: -30px; 
  transform: rotate(45deg);
  background-color: #34c759; 
  color: white;
  padding: 4px 30px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.tariff-card__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.tariff-card__image-wrapper {
  width: 60px;
  height: 60px;
}

.tariff-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.tariff-card__reward {
  line-height: 1.1;
}

.tariff-card__amount {
  font-size: 28px;
  font-weight: 700;
}

.tariff-card__currency {
  font-size: 15px;
  color: #8e8e93;
}

.tariff-card__footer {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px; 
  width: 100%;
}

.tariff-card__price {
  font-size: 17px;
  font-weight: 600;
  color: #e5e5e5;
}

.tariff-card__arrow {
  font-size: 18px;
  font-weight: 600;
  color: #8e8e93;
  transition: transform 0.2s ease, color 0.2s ease;
}

.tariff-card:hover .tariff-card__arrow {
  transform: translateX(4px);
  color: #fff;
}
</style>
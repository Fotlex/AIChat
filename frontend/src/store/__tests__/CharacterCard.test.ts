import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CharacterCard from '../CharacterCard.vue';

const globalConfig = {
  global: {
    stubs: {
      'i-local-heart': true
    }
  }
};

describe('CharacterCard.vue', () => {
  const character = {
    id: 1,
    name: 'Эльза',
    tagline: 'Снежная королева',
    likes_count: 1200,
    photo: null,
  };

  it('отображает имя и теглайн персонажа', () => {
    const wrapper = mount(CharacterCard, {
      props: { character },
      ...globalConfig
    });

    expect(wrapper.text()).toContain('Эльза');
    expect(wrapper.text()).toContain('Снежная королева');
  });

  it('правильно форматирует тысячи в "K" для лайков', () => {
    const wrapper = mount(CharacterCard, {
      props: { character },
      ...globalConfig
    });
    expect(wrapper.text()).toContain('1.2K');
  });

  it('эмитит событие select при клике', async () => {
    const wrapper = mount(CharacterCard, {
      props: { character },
      ...globalConfig
    });

    await wrapper.trigger('click');
    
    expect(wrapper.emitted()).toHaveProperty('select');
    expect(wrapper.emitted('select')?.[0]).toEqual([1]);
  });
});
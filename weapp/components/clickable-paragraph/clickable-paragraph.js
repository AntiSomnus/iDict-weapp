// components/clickable-paragraph/clickable-paragraph.js

function separate(str) {
  return str
    .split(/([a-zA-Z][a-zA-Z-]*[\.,?!;'\s]*)/g)
    .filter(n => n)
    .map(s => {
      const r = /[\.,?!;'\s]+$/.exec(s)
      if (r)
        return [s.slice(0, r.index), s.slice(r.index).replace(' ', '&nbsp;')]
      return s
    });

}
Component({
  /**
   * 组件的属性列表
   */
  externalClasses: ['text-class', 'custom-clicked', 'container-class'],
  data: {
    words: []
  },
  properties: {
    section: String,
    current: Object,
    data: String,
  },
  observers: {
    'data': function(data) {
      // 在 numberA 或者 numberB 被设置时，执行这个函数
      this.setData({
        words: separate(data)
      })
    }
  },
  /**
   * 组件的初始数据
   */

  methods: {
    clicked(e) {
      this.triggerEvent('clicked', e.target.dataset);
    }
  }
})
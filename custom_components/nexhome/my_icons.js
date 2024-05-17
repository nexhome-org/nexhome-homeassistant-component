class MyCustomIcon extends HTMLElement {
    constructor() {
      super();
      // 初始化组件
    }
  
    connectedCallback() {
      const iconUrl = '/local/icons/logo.svg'; // 确保路径正确
      this.innerHTML = `<img src="${iconUrl}" style="width: 24px; height: 24px;">`;
    }
  }
  
  customElements.define('my-custom-icon', MyCustomIcon);
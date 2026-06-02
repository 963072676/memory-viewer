declare module 'vue-virtual-scroller' {
  import type { DefineComponent, Plugin } from 'vue'

  export const RecycleScroller: DefineComponent<{
    items: any[]
    itemSize?: number | { default: number }
    direction?: 'vertical' | 'horizontal'
    gridItems?: number
    itemSecondarySize?: number
    keyField?: string
    listTag?: string
    itemTag?: string
    listClass?: string | object | any[]
    itemClass?: string | object | any[]
    buffer?: number
    pageMode?: boolean
    prerender?: number
    sizeField?: string
    typeField?: string
    emitUpdate?: boolean
    skipHover?: boolean
    minItemSize?: number
  }>

  export const DynamicScroller: DefineComponent<any>
  export const DynamicScrollerItem: DefineComponent<any>

  const VueVirtualScroller: Plugin
  export default VueVirtualScroller
}

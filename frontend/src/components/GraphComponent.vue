<template>
  <div class="graph-container">
    <svg
      :width="size"
      :height="size"
      viewBox="0 0 300 300"
      class="graph-svg"
      @click="handleClick"
    >
      <defs>
        <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
          <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="300" height="300" fill="url(#grid)" />

      <line x1="0" y1="150" x2="300" y2="150" stroke="#3d2817" stroke-width="2" />
      <line x1="150" y1="0" x2="150" y2="300" stroke="#3d2817" stroke-width="2" />

      <polygon points="295,150 285,145 285,155" fill="#3d2817" />
      <polygon points="150,5 145,15 155,15" fill="#3d2817" />

      <text x="290" y="145" fill="#3d2817" font-size="12" text-anchor="end">x</text>
      <text x="160" y="15" fill="#3d2817" font-size="12">y</text>

      <g v-if="r && r > 0">
        <rect
          :x="150 - scale(r)"
          :y="150"
          :width="scale(r)"
          :height="scale(r)"
          fill="#4169e1"
          fill-opacity="0.5"
          stroke="#4169e1"
          stroke-width="1"
        />

        <polygon
          :points="`${150},${150} ${150 - scale(r/2)},${150} ${150},${150 - scale(r)}`"
          fill="#4169e1"
          fill-opacity="0.5"
          stroke="#4169e1"
          stroke-width="1"
        />

        <path
          :d="`M ${150},${150 - scale(r/2)} A ${scale(r/2)},${scale(r/2)} 0 0,1 ${150 + scale(r/2)},${150} L ${150},${150} L ${150},${150 - scale(r/2)} Z`"
          fill="#4169e1"
          fill-opacity="0.5"
          stroke="#4169e1"
          stroke-width="1"
        />
      </g>

      <g>
        <text :x="150 - scale(5)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">-5</text>
        <text :x="150 - scale(4)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">-4</text>
        <text :x="150 - scale(3)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">-3</text>
        <text :x="150 - scale(2)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">-2</text>
        <text :x="150 - scale(1)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">-1</text>
        <text x="150" y="165" fill="#3d2817" font-size="10" text-anchor="middle">0</text>
        <text :x="150 + scale(1)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">1</text>
        <text :x="150 + scale(2)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">2</text>
        <text :x="150 + scale(3)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">3</text>
        <text :x="150 + scale(4)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">4</text>
        <text :x="150 + scale(5)" :y="165" fill="#3d2817" font-size="10" text-anchor="middle">5</text>

        <text :x="140" :y="150 + scale(5)" fill="#3d2817" font-size="10" text-anchor="end">-5</text>
        <text :x="140" :y="150 + scale(4)" fill="#3d2817" font-size="10" text-anchor="end">-4</text>
        <text :x="140" :y="150 + scale(3)" fill="#3d2817" font-size="10" text-anchor="end">-3</text>
        <text :x="140" :y="150 + scale(2)" fill="#3d2817" font-size="10" text-anchor="end">-2</text>
        <text :x="140" :y="150 + scale(1)" fill="#3d2817" font-size="10" text-anchor="end">-1</text>
        <text x="140" y="155" fill="#3d2817" font-size="10" text-anchor="end">0</text>
        <text :x="140" :y="150 - scale(1)" fill="#3d2817" font-size="10" text-anchor="end">1</text>
        <text :x="140" :y="150 - scale(2)" fill="#3d2817" font-size="10" text-anchor="end">2</text>
        <text :x="140" :y="150 - scale(3)" fill="#3d2817" font-size="10" text-anchor="end">3</text>

        <line :x1="150 - scale(5)" y1="145" :x2="150 - scale(5)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 - scale(4)" y1="145" :x2="150 - scale(4)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 - scale(3)" y1="145" :x2="150 - scale(3)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 - scale(2)" y1="145" :x2="150 - scale(2)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 - scale(1)" y1="145" :x2="150 - scale(1)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line x1="150" y1="145" x2="150" y2="155" stroke="#3d2817" stroke-width="2" />
        <line :x1="150 + scale(1)" y1="145" :x2="150 + scale(1)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 + scale(2)" y1="145" :x2="150 + scale(2)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 + scale(3)" y1="145" :x2="150 + scale(3)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 + scale(4)" y1="145" :x2="150 + scale(4)" y2="155" stroke="#3d2817" stroke-width="1" />
        <line :x1="150 + scale(5)" y1="145" :x2="150 + scale(5)" y2="155" stroke="#3d2817" stroke-width="1" />

        <line x1="145" :y1="150 + scale(5)" x2="155" :y2="150 + scale(5)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" :y1="150 + scale(4)" x2="155" :y2="150 + scale(4)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" :y1="150 + scale(3)" x2="155" :y2="150 + scale(3)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" :y1="150 + scale(2)" x2="155" :y2="150 + scale(2)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" :y1="150 + scale(1)" x2="155" :y2="150 + scale(1)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" y1="150" x2="155" y2="150" stroke="#3d2817" stroke-width="2" />
        <line x1="145" :y1="150 - scale(1)" x2="155" :y2="150 - scale(1)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" :y1="150 - scale(2)" x2="155" :y2="150 - scale(2)" stroke="#3d2817" stroke-width="1" />
        <line x1="145" :y1="150 - scale(3)" x2="155" :y2="150 - scale(3)" stroke="#3d2817" stroke-width="1" />
      </g>

      <circle
        v-for="(point, index) in points"
        :key="index"
        :cx="150 + scale(point.x)"
        :cy="150 - scale(point.y)"
        r="4"
        :fill="point.hit ? '#2e7d32' : '#d32f2f'"
        stroke="white"
        stroke-width="1"
        class="point"
      />
    </svg>
  </div>
</template>

<script>
export default {
  name: 'GraphComponent',
  props: {
    r: {
      type: Number,
      default: null
    },
    points: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      size: 300
    }
  },
  methods: {
    scale(value) {
      const maxValue = 5
      const maxPixels = 120
      return (value / maxValue) * maxPixels
    },
    handleClick(event) {
      if (!this.r || this.r === 0) return
      
      const svg = event.currentTarget
      const point = svg.createSVGPoint()
      point.x = event.clientX
      point.y = event.clientY
      
      const svgPoint = point.matrixTransform(svg.getScreenCTM().inverse())
      
      const pixelsPerUnit = this.scale(1)
      const graphX = (svgPoint.x - 150) / pixelsPerUnit
      const graphY = (150 - svgPoint.y) / pixelsPerUnit
      
      const roundedX = Math.round(graphX * 100) / 100
      const roundedY = Math.round(graphY * 100) / 100
      
      this.$emit('point-click', roundedX, roundedY)
    }
  }
}
</script>

<style scoped>
.graph-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.graph-svg {
  border: 1px solid #ddd;
  background: white;
  cursor: crosshair;
  max-width: 100%;
  height: auto;
}

.point {
  pointer-events: none;
}

@media (min-width: 753px) and (max-width: 1078px) {
  .graph-svg {
    width: 100%;
    max-width: 400px;
  }
}

@media (max-width: 752px) {
  .graph-svg {
    width: 100%;
    max-width: 100%;
  }
}
</style>


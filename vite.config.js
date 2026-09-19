// vite 开发服务器配置
// 解决：部分客户端（Windows 内置浏览器 / curl）会把中文路径先转成系统本地编码
// （GBK）再做 percent-encoding，产生一串"合法但非 UTF-8"的 %XX 序列。
// vite 内部 decodeURI() 按 UTF-8 解释这些字节，遇到非法 UTF-8 序列即抛出
// "URI malformed"（HTTP 500）。本中间件在 vite 内部处理之前规范化这类 URL：
//   1) 修补落单的 '%'；
//   2) URL 合法则原样放行；
//   3) 非法时把 %XX 还原成字节流，依次尝试 UTF-8 / GBK 解码，
//      再按 UTF-8 重新 percent-encode，使 vite 的文件查找能正常工作。
import { defineConfig } from 'vite'

function toBytes(url) {
  // %XX -> 对应字节；其余字符按 latin1（ASCII 原样）
  const latin = url.replace(/%([0-9A-Fa-f]{2})/g, (_, h) =>
    String.fromCharCode(parseInt(h, 16))
  )
  return Buffer.from(latin, 'latin1')
}

function reencode(str) {
  return Array.from(str)
    .map((ch) => (ch.codePointAt(0) < 128 ? ch : encodeURIComponent(ch)))
    .join('')
}

function decodeBytes(bytes) {
  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes)
  } catch {
    /* 非 UTF-8，继续尝试 */
  }
  try {
    return new TextDecoder('gbk').decode(bytes)
  } catch {
    /* 环境不支持 GBK 时保持原样 */
  }
  return null
}

function fixUrl(url) {
  if (!url) return url
  const s = url.replace(/%(?![0-9A-Fa-f]{2})/g, '%25')
  try {
    decodeURI(s) // 合法 UTF-8 编码：放行
    return s
  } catch {
    /* 进入修复流程 */
  }
  const decoded = decodeBytes(toBytes(s))
  return decoded === null ? s : reencode(decoded)
}

export default defineConfig({
  plugins: [
    {
      name: 'fix-legacy-encoded-request-url',
      configureServer(server) {
        server.middlewares.use((req, _res, next) => {
          try {
            req.url = fixUrl(req.url)
          } catch {
            /* 修复失败则维持原行为 */
          }
          next()
        })
      },
    },
  ],
})

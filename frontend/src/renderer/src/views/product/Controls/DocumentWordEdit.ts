import Quill from 'quill'
import mammoth from 'mammoth'
import QuillBetterTable from 'quill-better-table'

export class DocumentWordEdit {
  quill: Quill
  commands: any
  html: string
  constructor(el: string) {
    Quill.register(
      {
        'modules/better-table': QuillBetterTable
      },
      true
    )
    this.quill = new Quill(el, {
      theme: 'snow',
      modules: {
        table: false, // disable table module
        'better-table': {
          operationMenu: {
            items: {
              unmergeCells: {
                text: ''
              }
            }
          }
        },
        keyboard: {
          //@ts-ignore
          bindings: QuillBetterTable.keyboardBindings
        }
      }
    })
  }

  docxToQuill(file: File) {
    const reader = new FileReader()
    reader.onload = (loadEvent) => {
      // 使用 Mammoth 将 .docx 转换为 HTML
      mammoth
        .convertToHtml({
          // @ts-ignore
          arrayBuffer: loadEvent.target!.result,
          includeDefaultStyleMap: false,
          styleMap: {}
        })
        .then((result) => {
          this.html = result.value // 转换后的 HTML
          // 清空 Quill 编辑器的内容
          this.quill.setContents([])

          // 将 HTML 插入到 Quill 编辑器
          this.quill.clipboard.dangerouslyPasteHTML(this.html)
        })
        .catch((error) => {
          console.error('Error converting document: ', error)
        })
    }
    reader.readAsArrayBuffer(file)
  }
}

import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Tag {
  _id: {
    $oid: string
  }
  download_path: string
  files: {
    main_docx: {
      object_name: string
      file_name: string
      split_files: any[]
    }
  }
  _requirementFileList: any[]
  [p: string]: any
}
export const useTagsStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const current = ref<Tag | null>(null)

  const addTag = (tag: any) => {
    const index = tags.value.findIndex((item: any) => item._id.$oid === tag._id.$oid)
    if (index < 0) {
      tags.value.push(tag)
    } else {
      tags.value[index] = tag
    }
    current.value = tag
  }

  const removeTag = () => {
    const index = tags.value.findIndex((it) => it._id.$oid == current.value?._id.$oid)
    tags.value.splice(index, 1)
    current.value = tags.value[index] || tags.value[index - 1] || null
  }

  return {
    tags,
    current,
    addTag,
    removeTag
  }
})

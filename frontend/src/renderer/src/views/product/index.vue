<script lang="ts" setup>
import { Delete, Download, Plus, Search, Setting, ArrowRight } from '@element-plus/icons-vue'
import AddOrUpdate from '@renderer/views/product/AddOrUpdate.vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTagsStore } from '../../stores/useTagsStore'
import { useProductFetch } from './useProductFetch'
import DownloadFileCard from './Controls/DownloadFileCard.vue'
import { ElMessageBox } from 'element-plus'
import DirectionTreeNode from '../../components/DirectionTreeNode/index.vue'
import { http } from '@renderer/http'

const { formData, handler, tableData } = useProductFetch()

handler.List().then()

const dialogVisible = ref(false)

const router = useRouter()
const store = useTagsStore()
const onClickProductItem = (item: any) => {
  handler.Detail(item._id.$oid).then((detail) => {
    store.addTag(detail)
    router.push('/controls')
  })
}
const onShowDownload = (item) => {
  store.current = item
}
const onDelete = async (item: any) => {
  ElMessageBox.confirm('是否删除？', '提示', {
    confirmButtonText: '是',
    cancelButtonText: '否',
    type: 'warning'
  }).then(async () => {
    await handler.Delete(item._id.$oid)
    await handler.List()
  })
}

const settingDialogVisible = ref(false)
const currentItem = ref({})

const onSetting = (item) => {
  console.log(item);
  currentItem.value = { ...item }
  settingDialogVisible.value = true
}

const saveSettings = () => {
  // 在这里处理保存设置的逻辑
  console.log('保存设置:', currentItem.value)
  settingDialogVisible.value = false
  http.post('/api/update_storage_path', {
    project_id: currentItem.value._id.$oid,
    storage_path: currentItem.value.storage_path,
    download_path: currentItem.value.download_path
  }).then(() => {
    handler.List().then()
  })
}
</script>

<template>
  <div class="product-container">
    <el-input v-model="formData.search" class="search-input" placeholder="搜索项目..." @blur="handler.List">
      <template #prefix>
        <el-icon>
          <Search />
        </el-icon>
      </template>
    </el-input>
    <div class="flex items-center justify-between mb-[20px]">
      <h1 class="text-[20px] text-[#333]">项目总数({{ tableData.length }})</h1>
      <el-button type="primary" @click="dialogVisible = true">
        <el-icon class="mr-[5px]">
          <Plus />
        </el-icon>
        创建项目
      </el-button>
    </div>
    <div v-if="tableData.length" class="grid grid-cols-4 gap-[18px]">
      <div v-for="item in tableData" :key="item" class="product-item" @click="onClickProductItem(item)">
        <div class="flex gap-[8px]">
          <img alt="" class="w-[68px] h-[68px]" src="/images/product-icon.png" />
          <div class="text-[12px] text-[#999] flex flex-col gap-[4px]">
            <h1 class="text-[16px] text-[#333]">{{ item.name }}</h1>
            <p>ID：{{ item.display_id }}</p>
            <p>更新时间：{{ item._update_at }}</p>
            <div class="card-tool">
              <el-popover trigger="hover" width="240px" @show="() => onShowDownload(item)">
                <template #reference>
                  <el-icon size="20">
                    <Download />
                  </el-icon>
                </template>
                <DownloadFileCard />
              </el-popover>
              <el-icon size="20" @click.stop="onDelete(item)">
                <Delete />
              </el-icon>
              <el-icon size="20" @click.stop="onSetting(item)">
                <Setting />
              </el-icon>
              <!--              <el-popover :key="item._id.$oid" trigger="click" width="280px">-->
              <!--                <template #reference>-->
              <!--                  <el-icon size="20"><Setting /></el-icon>-->
              <!--                </template>-->
              <!--                <div class="flex items-center">-->
              <!--                  <h5 class="text-[14px] whitespace-nowrap">项目存储路径：</h5>-->
              <!--                  <DirectionTreeNode v-model="item._savePath" kind="storage_path" />-->
              <!--                </div>-->
              <!--                <div class="flex items-center mt-[8px]">-->
              <!--                  <h5 class="text-[14px] whitespace-nowrap">下载文件路径：</h5>-->
              <!--                  <DirectionTreeNode v-model="item._downloadPath" kind="download_path" />-->
              <!--                </div>-->
              <!--              </el-popover>-->
            </div>
          </div>
        </div>
        <p class="text-[#999] text-[14px] clamp-1 mb-[40px] mt-[10px] h-[21px]">
          {{ item.notes || '暂无描述~' }}
        </p>
        <el-steps :active="item._active" align-center style="max-width: 600px">
          <el-step title="需求配置">
            <template #icon>
              <div class="origin-icon"></div>
            </template>
          </el-step>
          <el-step title="测试配置">
            <template #icon>
              <div class="origin-icon"></div>
            </template>
          </el-step>
          <el-step title="测试脚本">
            <template #icon>
              <div class="origin-icon"></div>
            </template>
          </el-step>
        </el-steps>
        <div class="flex items-center justify-around mt-[24px]">
          <span :class="{ 'is-success': [1, 2].includes(item.status.test_requirements) }" class="status-text">
            {{ ['未上传', '已上传', '已处理'][item.status?.test_requirements] || '未知错误' }}
          </span>
          <span :class="{ 'is-success': [1, 2].includes(item.status.test_cases) }" class="status-text">
            {{
              ['未处理', '处理中', '已处理', '未知错误', '已取消'][item.status?.test_cases] ||
              '未知错误'
            }}
          </span>
          <span :class="{ 'is-success': [1, 2].includes(item.status.test_scripts) }" class="status-text">
            {{
              ['未处理', '处理中', '已处理', '待处理', '出错了', '已取消'][
              item.status?.test_scripts
              ] || '未知错误'
            }}
          </span>
        </div>
      </div>
    </div>
    <el-empty v-else class="mt-[100px]" description="暂无数据">
      <template #image>
        <img alt="" class="w-[100px]!" src="/svgs/empty.svg" />
      </template>
    </el-empty>
  </div>
  <el-dialog v-model="dialogVisible" destroy-on-close title="创建项目" width="540">
    <AddOrUpdate @on-close="dialogVisible = false" @on-success="handler.List()" />
  </el-dialog>
  <el-dialog v-model="settingDialogVisible" title="设置" width="540">
    <el-form :model="currentItem" label-width="120px">
      <el-form-item label="存储路径">
        <DirectionTreeNode
          v-model="currentItem.storage_path"
          :suffix-icon="ArrowRight"
          class="w-full!"
          kind="storage_path"
        />
      </el-form-item>
      <el-form-item label="下载路径">
        <DirectionTreeNode
          v-model="currentItem.download_path"
          :suffix-icon="ArrowRight"
          class="w-full!"
          kind="download_path"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="settingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style lang="scss">
.product-container {
  margin: 20px;
  padding: 16px;

  .search-input {
    position: fixed;
    right: 32px;
    top: 66px;
    width: 200px;
  }

  .product-item {
    height: 268px;
    border-radius: 4px;
    background: #fff;
    box-shadow: 0 0 0 0 rgba(42, 1, 61, 0);
    padding: 18px;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    border: 1px solid #e3e3e3;

    &:hover {
      box-shadow: 0 4px 20px 0 rgba(42, 1, 61, 0.18);
      background: url('/images/product-bg.png') no-repeat;
      background-size: 100% 100%;
    }
  }

  .card-tool {
    position: absolute;
    top: 20px;
    right: 10px;
    display: flex;
    gap: 4px;
  }

  .el-step__icon {
    background: transparent;
  }

  .el-step__title {
    line-height: 20px;
    font-size: 14px;
  }

  .origin-icon {
    width: 8px;
    height: 8px;
    border: 2px solid #fef7ff;
    border-radius: 50%;
    background: #c8c8c8;
  }

  .is-finish {
    color: #333 !important;

    .origin-icon {
      background: #4060f8;
    }
  }

  .is-process {
    color: #999 !important;
  }

  .status-text {
    width: 52px;
    height: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    background: #f7f8fa;
    color: rgba(134, 144, 156, 1);
    font-size: 12px;

    &.is-success {
      background: #e8ffea;
      color: #00b42a;
    }
  }
}
</style>

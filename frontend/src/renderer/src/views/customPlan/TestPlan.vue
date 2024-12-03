<template>
    <div style="display: flex; height: 100%; width: 100%">
        <!-- 中间 -->
        <a-card title="测评方案" style="height: 100%; width: 100%">
            <a-tree :tree-data="treeData" v-model:selectedKeys="selectedKeys" @select="onSelect">
                <template #title="{ title, key }">
                    <span>{{ title }}</span>
                    <span style="float: right; margin-left: 10px;">
                        <a-button type="link" @click.stop="showEditModal(key)">
                            <edit-outlined />
                        </a-button>
                        <a-button type="link" @click.stop="confirmDeletePlan(key)">
                            <delete-outlined />
                        </a-button>
                    </span>
                </template>
            </a-tree>
            <a-button type="dashed" block @click="showAddModal" style="margin-top: 20px;">添加方案</a-button>
        </a-card>

        <!-- 添加方案的弹窗 -->
        <a-modal v-model:visible="addModalVisible" title="添加方案" @ok="handleAddPlan">
            <a-input v-model:value="newPlanName" placeholder="请输入方案名称" />
        </a-modal>

        <!-- 编辑方案的弹窗 -->
        <a-modal v-model:visible="editModalVisible" title="编辑方案" @ok="handleEditPlan">
            <a-input v-model:value="editingPlanName" placeholder="请输入方案名称" />
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { http } from '@renderer/http';
import { EditOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import { Modal } from 'ant-design-vue';
import { ElButton, ElMessage } from 'element-plus'
const props = defineProps<{
    project_id: string;
    selectedKeys: string[];
}>();

const emit = defineEmits<{
    (e: 'planChange', planId: string): void;
}>();

const treeData = ref([
    {
        title: '方案1',
        key: 'plan-1',
    },
    {
        title: '方案2',
        key: 'plan-2',
    },
    {
        title: '方案3',
        key: 'plan-3',
    },
]);

const addModalVisible = ref(false);
const editModalVisible = ref(false);
const newPlanName = ref('');
const editingPlanName = ref('');
const editingPlanKey = ref('');

const selectedKeys = ref<string[]>([]);

onMounted(async () => {
    await fetchPlanList();
    if (treeData.value.length > 0) {
        selectedKeys.value = [treeData.value[0].key];
        emit('planChange', treeData.value[0].key);
    } else {
        emit('planChange', 'plan-1');
    }
});

const fetchPlanList = async () => {
    const response = await http.post('/test_project/get_plan_list', {
        project_id: props.project_id
    });
    treeData.value = response.data.map(item => ({
        title: item.plan_name,
        key: item.plan_id,
    }));
    return response;
};

const showAddModal = () => {
    addModalVisible.value = true;
};

const showEditModal = (key) => {
    editingPlanKey.value = key;
    const plan = treeData.value.find(item => item.key === key);
    editingPlanName.value = plan.title;
    editModalVisible.value = true;
};

const handleAddPlan = async () => {
    const noPlan = !treeData.value.length;
    const payload = {
        project_id: props.project_id,
        plan_name: newPlanName.value,
    };
    if (!payload.plan_name) {
        ElMessage.error('方案名称不能为空');
        return;
    }
    const response = await http.post('/test_project/create_plan', payload);
    const result = await fetchPlanList();
    addModalVisible.value = false;
    newPlanName.value = '';

    // 获取新创建的方案的 key
    if (noPlan) {
        console.log(result);
        const first = result.data[0];
        selectedKeys.value = [first.plan_id];
        emit('planChange', first.plan_id);
    }

};

const handleEditPlan = async () => {
    const payload = {
        plan_id: editingPlanKey.value,
        plan_name: editingPlanName.value,
    };
    await http.post('/test_project/update_plan', payload);
    await fetchPlanList();
    editModalVisible.value = false;
    editingPlanName.value = '';
};

const confirmDeletePlan = (key) => {
    Modal.confirm({
        title: '确认删除',
        content: '确定要删除该方案吗？',
        onOk: () => deletePlan(key),
        onCancel() { },
    });
};

const deletePlan = async (key) => {
    const payload = {
        plan_id: key,
    };
    await http.post('/test_project/delete_plan', payload);
    await fetchPlanList();
};

const onSelect = (selectedKeys, info) => {
    console.log('selected', selectedKeys, info);
    if (selectedKeys.length > 0) {
        emit('planChange', selectedKeys[0]);
    }
};

watch(
    () => props.selectedKeys,
    (newSelectedKeys) => {
        selectedKeys.value = newSelectedKeys;
    },
    { immediate: true }
);
</script>

<style scoped>
/* Add your custom styles here */
</style>
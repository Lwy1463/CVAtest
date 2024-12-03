<template>
    <div style="margin: 20px;">
        <a-page-header title="测试项目管理" />
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <a-input-search v-model:value="searchText" placeholder="请输入项目名称" style="width: 200px"
                @search="fetchTestProjectList" />
            <a-button type="primary" @click="showCreateModal"> 新增测试项目 </a-button>
        </div>

        <a-table :columns="columns" :dataSource="testProjectList" :rowKey="record => record.project_id"
            :pagination="paginationConfig" :scroll="{ y: table_height }">
            <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'action'">
                    <a-button type="link" style="color: #de8dcc" @click="deleteTestProject(record.project_id)">删除</a-button>
                    <a-divider type="vertical" />
                    <a-button type="link" style="color: #de8dcc"  @click="showConfigModal(record)">修改</a-button>
                    <a-divider type="vertical" />
                    <a-button type="link" style="color: #de8dcc" @click="gotoConfig(record)">配置</a-button>
                    <a-divider type="vertical" />
                    <a-button type="link" style="color: #de8dcc" @click="executeTestProject(record)">执行</a-button>
                </template>
            </template>
        </a-table>

        <a-modal title="新增测试项目" v-model:visible="createModalVisible" @ok="createTestProject" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="createForm" :model="createFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="项目名称" name="project_name">
                        <a-input v-model:value="createFormData.project_name" />
                    </a-form-item>
                    <a-form-item label="项目编号" name="project_code">
                        <a-input v-model:value="createFormData.project_code" />
                    </a-form-item>
                    <a-form-item label="项目描述" name="description">
                        <a-input v-model:value="createFormData.description" />
                    </a-form-item>
                    <a-form-item label="测试对象名称" name="test_object_name">
                        <a-input v-model:value="createFormData.test_object_name" />
                    </a-form-item>
                    <a-form-item label="测试对象版本" name="test_object_version">
                        <a-input v-model:value="createFormData.test_object_version" />
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>

        <a-modal title="修改测试项目" v-model:visible="configModalVisible" @ok="updateTestProject" @cancel="handleCancel" okText="确定"
            cancelText="取消" width="60%">
            <a-form ref="configForm" :model="configFormData" :rules="rules">
                <div class="modal-form-grid">
                    <a-form-item label="项目名称" name="project_name">
                        <a-input v-model:value="configFormData.project_name" />
                    </a-form-item>
                    <a-form-item label="项目编号" name="project_code">
                        <a-input v-model:value="configFormData.project_code" />
                    </a-form-item>
                    <a-form-item label="项目描述" name="description">
                        <a-input v-model:value="configFormData.description" />
                    </a-form-item>
                    <a-form-item label="测试对象名称" name="test_object_name">
                        <a-input v-model:value="configFormData.test_object_name" />
                    </a-form-item>
                    <a-form-item label="测试对象版本" name="test_object_version">
                        <a-input v-model:value="configFormData.test_object_version" />
                    </a-form-item>
                </div>
            </a-form>
        </a-modal>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { http } from '@renderer/http';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { useProjectStore } from '@renderer/stores/useProject';
import { storeToRefs } from 'pinia';

const projectStore = useProjectStore();
const { projectDetail } = storeToRefs(projectStore);
const searchText = ref('');
const testProjectList = ref([]);
const createModalVisible = ref(false);
const configModalVisible = ref(false);
const createForm = ref(null);
const configForm = ref(null);

const createFormData = reactive({
    project_name: '',
    project_code: '',
    description: '',
    test_object_name: '',
    test_object_version: '',
});

const configFormData = reactive({
    project_id: '',
    project_name: '',
    project_code: '',
    description: '',
    test_object_name: '',
    test_object_version: '',
});

const columns = [
    { title: '序号', dataIndex: 'project_id' },
    { title: '项目名称', dataIndex: 'project_name' },
    { title: '项目编号', dataIndex: 'project_code' },
    { title: '项目描述', dataIndex: 'description' },
    { title: '测试对象名称', dataIndex: 'test_object_name' },
    { title: '测试对象版本', dataIndex: 'test_object_version' },
    {
        title: '操作',
        key: 'action',
        scopedSlots: { customRender: 'action' },
    },
];

const paginationConfig = reactive({
    total: 1000,
    pageSize: 100,
    current: 1,
    onChange: (page, pageSize) => {
        paginationConfig.current = page;
        paginationConfig.pageSize = pageSize;
        fetchTestProjectList();
    },
});

onMounted(() => {
    fetchTestProjectList();
});

const fetchTestProjectList = async () => {
    const params = {
        project_name: searchText.value || void 0,
    };
    const data = await http.post('/test_project/get_test_project_list', params);
    testProjectList.value = data.data;
    paginationConfig.total = data.total;
};

const showCreateModal = () => {
    createModalVisible.value = true;
    createFormData.project_name = '';
    createFormData.project_code = '';
    createFormData.description = '';
    createFormData.test_object_name = '';
    createFormData.test_object_version = '';
};

const showConfigModal = (record) => {
    configFormData.project_id = record.project_id;
    configFormData.project_name = record.project_name;
    configFormData.project_code = record.project_code;
    configFormData.description = record.description;
    configFormData.test_object_name = record.test_object_name;
    configFormData.test_object_version = record.test_object_version;
    configModalVisible.value = true;
};

const router = useRouter();
const gotoConfig = (record) => {
    projectStore.setProjectDetail(record);
    console.log(projectStore);
    router.push('/customPlan');
};

const createTestProject = () => {
    if (!createFormData.project_name) {
        ElMessage.error('请填写项目名称');
        return;
    }
    
    createForm.value.validate().then(async () => {
        await http.post('/test_project/create_test_project', createFormData);
        createModalVisible.value = false;
        fetchTestProjectList();
    });
};

const updateTestProject = () => {
    if (!configFormData.project_name) {
        ElMessage.error('请填写项目名称');
        return;
    }
    configForm.value.validate().then(async () => {
        await http.post('/test_project/update_test_project', configFormData);
        configModalVisible.value = false;
        fetchTestProjectList();
    });
};

const deleteTestProject = async (project_id) => {
    const confirmResult = await ElMessageBox.confirm(
        '确定要删除该测试项目吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    );

    if (confirmResult) {
        await http.post('/test_project/delete_test_project', { project_id });
        fetchTestProjectList();
    }
};

const executeTestProject = async (record) => {
    projectStore.setProjectDetail(record);
    router.push('/execution');
};

const handleCancel = () => {
    createModalVisible.value = false;
    configModalVisible.value = false;
};

const table_height = window.innerHeight * 0.55;

const rules = {
    project_name: [{ required: true, message: '请填写项目名称', trigger: 'change' }],
    project_code: [{ required: true, message: '请填写项目编号', trigger: 'change' }],
    test_object_name: [{ required: true, message: '请填写测试对象名称', trigger: 'change' }],
    test_object_version: [{ required: true, message: '请填写测试对象版本', trigger: 'change' }],
};
</script>

<style scoped>
.modal-form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 20px;
}
</style>
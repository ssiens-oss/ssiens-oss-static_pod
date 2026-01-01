/**
 * Projects Page
 * Manage and organize music projects
 */

import { useState } from 'react';
import { FolderOpen, Plus, Trash2, Edit2, Music, Calendar, Clock } from 'lucide-react';
import useStore from '../store';
import { Card, Button, Modal, Input, Badge } from '../components';

const ProjectsPage = () => {
  const projects = useStore((state) => state.projects);
  const currentProject = useStore((state) => state.currentProject);
  const createProject = useStore((state) => state.createProject);
  const updateProject = useStore((state) => state.updateProject);
  const deleteProject = useStore((state) => state.deleteProject);
  const setCurrentProject = useStore((state) => state.setCurrentProject);
  const addNotification = useStore((state) => state.addNotification);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectType, setNewProjectType] = useState('song');

  const handleCreateProject = () => {
    if (!newProjectName.trim()) {
      addNotification({
        type: 'error',
        message: 'Project name is required'
      });
      return;
    }

    createProject(newProjectName, newProjectType);
    setNewProjectName('');
    setNewProjectType('song');
    setShowCreateModal(false);
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setNewProjectName(project.name);
    setNewProjectType(project.type);
    setShowEditModal(true);
  };

  const handleUpdateProject = () => {
    if (!newProjectName.trim()) {
      addNotification({
        type: 'error',
        message: 'Project name is required'
      });
      return;
    }

    updateProject(editingProject.id, {
      name: newProjectName,
      type: newProjectType
    });

    setEditingProject(null);
    setNewProjectName('');
    setNewProjectType('song');
    setShowEditModal(false);

    addNotification({
      type: 'success',
      message: 'Project updated successfully'
    });
  };

  const handleDeleteProject = (projectId, projectName) => {
    if (window.confirm(`Are you sure you want to delete "${projectName}"?`)) {
      deleteProject(projectId);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const projectTypes = [
    { id: 'song', name: 'Song', icon: Music },
    { id: 'freestyle', name: 'Freestyle', icon: Music },
    { id: 'battle', name: 'Battle', icon: Music }
  ];

  const getProjectIcon = (type) => {
    const projectType = projectTypes.find((t) => t.id === type);
    return projectType ? projectType.icon : Music;
  };

  const getProjectColor = (type) => {
    const colors = {
      song: 'primary',
      freestyle: 'success',
      battle: 'error'
    };
    return colors[type] || 'default';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <FolderOpen className="w-8 h-8 text-accent" />
            Projects
          </h1>
          <p className="text-gray-400 mt-2">
            {projects.length === 0
              ? 'No projects yet. Create one to get started!'
              : `${projects.length} project${projects.length !== 1 ? 's' : ''}`}
          </p>
        </div>

        <Button
          onClick={() => setShowCreateModal(true)}
          icon={<Plus className="w-5 h-5" />}
        >
          New Project
        </Button>
      </div>

      {/* Current Project Banner */}
      {currentProject && (
        <Card variant="gradient" className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center">
                <Music className="w-6 h-6 text-accent" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Current Project</p>
                <h3 className="text-xl font-bold">{currentProject.name}</h3>
              </div>
            </div>
            <Badge variant={getProjectColor(currentProject.type)}>
              {currentProject.type}
            </Badge>
          </div>
        </Card>
      )}

      {/* Project Grid */}
      {projects.length === 0 ? (
        <Card className="p-12 text-center">
          <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Projects Yet</h3>
          <p className="text-gray-400 mb-6">
            Create your first project to start organizing your music creations
          </p>
          <Button
            onClick={() => setShowCreateModal(true)}
            icon={<Plus className="w-5 h-5" />}
          >
            Create First Project
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => {
            const ProjectIcon = getProjectIcon(project.type);
            const isActive = currentProject?.id === project.id;

            return (
              <Card
                key={project.id}
                hover
                className={`p-5 ${isActive ? 'border-accent' : ''}`}
                onClick={() => setCurrentProject(project)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 bg-${isActive ? 'accent' : 'secondary'} rounded-lg flex items-center justify-center`}>
                      <ProjectIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{project.name}</h3>
                      <Badge size="sm" variant={getProjectColor(project.type)}>
                        {project.type}
                      </Badge>
                    </div>
                  </div>

                  {isActive && (
                    <Badge variant="success" size="sm">
                      Active
                    </Badge>
                  )}
                </div>

                <div className="space-y-2 mb-4 text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>Created {formatDate(project.createdAt)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>Updated {formatDate(project.updatedAt)}</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditProject(project);
                    }}
                    icon={<Edit2 className="w-4 h-4" />}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project.id, project.name);
                    }}
                    icon={<Trash2 className="w-4 h-4" />}
                  >
                    Delete
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create Project Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Project"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateProject}>Create Project</Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Project Name"
            placeholder="My Awesome Track"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Project Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {projectTypes.map((type) => {
                const TypeIcon = type.icon;
                return (
                  <button
                    key={type.id}
                    onClick={() => setNewProjectType(type.id)}
                    className={`p-4 rounded-lg border transition-all ${
                      newProjectType === type.id
                        ? 'border-accent bg-accent/10'
                        : 'border-white/10 hover:border-white/20'
                    }`}
                  >
                    <TypeIcon className="w-6 h-6 mx-auto mb-2" />
                    <p className="text-sm font-medium">{type.name}</p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </Modal>

      {/* Edit Project Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Edit Project"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowEditModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateProject}>Save Changes</Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Project Name"
            placeholder="My Awesome Track"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Project Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {projectTypes.map((type) => {
                const TypeIcon = type.icon;
                return (
                  <button
                    key={type.id}
                    onClick={() => setNewProjectType(type.id)}
                    className={`p-4 rounded-lg border transition-all ${
                      newProjectType === type.id
                        ? 'border-accent bg-accent/10'
                        : 'border-white/10 hover:border-white/20'
                    }`}
                  >
                    <TypeIcon className="w-6 h-6 mx-auto mb-2" />
                    <p className="text-sm font-medium">{type.name}</p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ProjectsPage;

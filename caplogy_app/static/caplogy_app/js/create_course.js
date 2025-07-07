document.addEventListener('DOMContentLoaded', () => {
    // Gestion des catégories en cascade
    const categorySelects = [
        document.getElementById('cat-level-0'),
        document.getElementById('cat-level-1'),
        document.getElementById('cat-level-2')
    ];

    // Charger les catégories principales
    loadCategories(0, categorySelects[0]);

    // Gestionnaires d'événements pour les sélecteurs de catégories
    categorySelects.forEach((select, index) => {
        select.addEventListener('change', (e) => {
            handleCategoryChange(index, e.target.value);
        });
    });

    function loadCategories(parentId, selectElement) {
        const url = parentId === 0 
            ? '/api/categories/' 
            : `/api/categories/?parent=${parentId}`;
            
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                selectElement.innerHTML = '<option value="">Sélectionnez...</option>';
                const categories = data.categories || data;
                categories.forEach(category => {
                    const option = new Option(category.name, category.id);
                    selectElement.add(option);
                });
            })
            .catch(error => {
                selectElement.innerHTML = '<option value="">Erreur de chargement</option>';
            });
    }

    function handleCategoryChange(level, categoryId) {
        // Masquer et vider les niveaux suivants
        for (let i = level + 1; i < categorySelects.length; i++) {
            categorySelects[i].classList.add('hidden');
            categorySelects[i].innerHTML = '<option value="">Sélectionnez...</option>';
        }

        // Si une catégorie est sélectionnée, charger les sous-catégories
        if (categoryId && categorySelects[level + 1]) {
            const url = `/api/categories/?parent=${categoryId}`;
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const categories = data.categories || data;
                    if (categories.length > 0) {
                        const nextSelect = categorySelects[level + 1];
                        nextSelect.classList.remove('hidden');
                        nextSelect.innerHTML = '<option value="">Sélectionnez...</option>';
                        categories.forEach(category => {
                            const option = new Option(category.name, category.id);
                            nextSelect.add(option);
                        });
                    }
                })
                .catch(error => {
                    // Erreur silencieuse
                });
        }
    }

    // Gestion des sections
    const sectionsList = document.getElementById('sections-list');
    const addSectionBtn = document.getElementById('add-section');
    let sectionCounter = 0;

    addSectionBtn.addEventListener('click', addNewSection);

    function addNewSection() {
        sectionCounter++;
        const sectionItem = createSectionElement(sectionCounter);
        sectionsList.appendChild(sectionItem);
        
        // Animation d'apparition
        setTimeout(() => {
            sectionItem.style.opacity = '1';
            sectionItem.style.transform = 'translateY(0)';
        }, 10);

        // Focus sur le champ titre
        const titleInput = sectionItem.querySelector('.section-title-input');
        titleInput.focus();
    }

    function createSectionElement(sectionNumber) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section-item';
        sectionDiv.style.opacity = '0';
        sectionDiv.style.transform = 'translateY(-20px)';
        sectionDiv.style.transition = 'all 0.3s ease';
        
        sectionDiv.innerHTML = `
            <div class="section-header-item">
                <div class="section-number">${sectionNumber}</div>
                <input type="text" 
                       name="section_${sectionNumber}" 
                       placeholder="Titre de la section ${sectionNumber}" 
                       required 
                       class="section-title-input">
                <button type="button" class="delete-section-btn" onclick="deleteSection(this)">
                    ✕
                </button>
            </div>
            <div class="section-actions">
                <button type="button" class="resource-btn" onclick="addResource(this, ${sectionNumber})">
                    Ajouter une ressource
                </button>
                <input type="hidden" name="file_${sectionNumber}" id="file_${sectionNumber}">
                <span class="selected-file" id="selected-file-${sectionNumber}"></span>
            </div>
        `;
        
        return sectionDiv;
    }

    // Fonction globale pour supprimer une section
    window.deleteSection = function(deleteBtn) {
        const sectionItem = deleteBtn.closest('.section-item');
        
        // Animation de disparition
        sectionItem.style.opacity = '0';
        sectionItem.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            sectionItem.remove();
            updateSectionNumbers();
        }, 300);
    };

    // Fonction globale pour ajouter une ressource
    window.addResource = function(btn, sectionId) {
        currentSectionId = sectionId;
        currentResourceBtn = btn;
        openFileModal('/');
    };

    function updateSectionNumbers() {
        const sections = sectionsList.querySelectorAll('.section-item');
        sections.forEach((section, index) => {
            const number = index + 1;
            const numberElement = section.querySelector('.section-number');
            const titleInput = section.querySelector('.section-title-input');
            const hiddenInput = section.querySelector('input[type="hidden"]');
            const selectedFile = section.querySelector('.selected-file');
            
            numberElement.textContent = number;
            titleInput.name = `section_${number}`;
            titleInput.placeholder = `Titre de la section ${number}`;
            hiddenInput.name = `file_${number}`;
            hiddenInput.id = `file_${number}`;
            selectedFile.id = `selected-file-${number}`;
        });
        sectionCounter = sections.length;
    }

    // Gestion de la modal de fichiers
    const modal = document.getElementById('nc-modal');
    const modalClose = document.getElementById('nc-close');
    const fileList = document.getElementById('nc-list');
    let currentSectionId = null;
    let currentResourceBtn = null;

    modalClose.addEventListener('click', closeFileModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeFileModal();
        }
    });

    function openFileModal(path) {
        modal.classList.add('active');
        loadFiles(path);
    }

    function closeFileModal() {
        modal.classList.remove('active');
        currentSectionId = null;
        currentResourceBtn = null;
    }

    function loadFiles(path) {
        fileList.innerHTML = '<li style="text-align: center; padding: 2rem; color: #6b7280;">🔄 Chargement...</li>';
        
        fetch(`/nc_dir/?path=${encodeURIComponent(path)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                fileList.innerHTML = '';
                
                // Ajouter le dossier parent si on n'est pas à la racine
                if (path !== '/') {
                    const parentPath = path.replace(/\/[^\/]*\/$/, '/');
                    const parentItem = document.createElement('li');
                    parentItem.innerHTML = '📁 .. (Dossier parent)';
                    parentItem.dataset.type = 'folder';
                    parentItem.dataset.path = parentPath;
                    parentItem.style.fontWeight = 'bold';
                    parentItem.style.color = '#3b82f6';
                    fileList.appendChild(parentItem);
                }

                // Ajouter les dossiers
                if (data.folders) {
                    data.folders.forEach(folderName => {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = `📁 ${folderName}`;
                        listItem.dataset.type = 'folder';
                        listItem.dataset.path = path + folderName + '/';
                        listItem.style.fontWeight = '500';
                        fileList.appendChild(listItem);
                    });
                }

                // Ajouter les fichiers
                if (data.files) {
                    data.files.forEach(fileName => {
                        const listItem = document.createElement('li');
                        const fileIcon = getFileIcon(fileName);
                        listItem.innerHTML = `${fileIcon} ${fileName}`;
                        listItem.dataset.type = 'file';
                        listItem.dataset.path = path + fileName;
                        fileList.appendChild(listItem);
                    });
                }

                if (fileList.children.length === 0) {
                    fileList.innerHTML = '<li style="text-align: center; padding: 2rem; color: #6b7280;">📂 Dossier vide</li>';
                }
            })
            .catch(error => {
                fileList.innerHTML = `<li style="text-align: center; padding: 2rem; color: #ef4444;">❌ ${error.message}</li>`;
            });
    }

    function getFileIcon(fileName) {
        const extension = fileName.split('.').pop().toLowerCase();
        const iconMap = {
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'xls': '📊',
            'xlsx': '📊',
            'ppt': '📽️',
            'pptx': '📽️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
            'mp4': '🎥',
            'mp3': '🎵',
            'zip': '🗜️',
            'rar': '🗜️',
            'txt': '📄'
        };
        return iconMap[extension] || '🔗';
    }

    // Gestionnaire de clic pour la liste des fichiers
    fileList.addEventListener('click', (e) => {
        const listItem = e.target.closest('li');
        if (!listItem || !listItem.dataset.type) return;

        const { type, path } = listItem.dataset;

        if (type === 'folder') {
            loadFiles(path);
        } else if (type === 'file') {
            selectFile(path);
        }
    });

    function selectFile(filePath) {
        if (currentSectionId && currentResourceBtn) {
            const fileName = filePath.split('/').pop();
            const hiddenInput = document.getElementById(`file_${currentSectionId}`);
            const selectedFileSpan = document.getElementById(`selected-file-${currentSectionId}`);
            
            hiddenInput.value = filePath;
            selectedFileSpan.textContent = `${fileName}`;
            selectedFileSpan.style.color = '#10b981';
            selectedFileSpan.style.fontWeight = '500';
            
            currentResourceBtn.textContent = `✅ ${fileName}`;
            currentResourceBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        }
        closeFileModal();
    }

    // Gestion de la soumission du formulaire
    document.getElementById('course-form').addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Validation basique
        const title = document.getElementById('title').value.trim();
        if (!title) {
            alert('⚠️ Veuillez saisir un titre pour le cours');
            return;
        }

        const sections = sectionsList.querySelectorAll('.section-item');
        if (sections.length === 0) {
            const confirmCreate = confirm('❓ Aucune section n\'a été créée. Voulez-vous créer le cours sans section ?');
            if (!confirmCreate) return;
        }

        // Validation des sections
        let hasEmptySection = false;
        sections.forEach(section => {
            const titleInput = section.querySelector('.section-title-input');
            if (!titleInput.value.trim()) {
                hasEmptySection = true;
            }
        });

        if (hasEmptySection) {
            alert('⚠️ Toutes les sections doivent avoir un titre');
            return;
        }

        // Animation du bouton de soumission
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        const loadingText = window.isEdit ? '⏳ Modification en cours...' : '⏳ Création en cours...';
        submitBtn.innerHTML = loadingText;
        submitBtn.disabled = true;

        // Soumission du formulaire
        setTimeout(() => {
            e.target.submit();
        }, 500);
    });

    // Initialisation pour le mode édition
    function initEditMode() {
        if (window.isEdit) {
            const courseDataElement = document.getElementById('course-data');
            if (courseDataElement) {
                const courseData = {
                    id: parseInt(courseDataElement.dataset.id),
                    categoryid: parseInt(courseDataElement.dataset.categoryid),
                    fullname: courseDataElement.dataset.fullname,
                    shortname: courseDataElement.dataset.shortname
                };
                
                // Validation des données
                if (!courseData.categoryid || courseData.categoryid === 0) {
                    return;
                }
                
                // Stocker les données globalement pour un accès facile
                window.courseData = courseData;
                
                // Charger les sections existantes
                loadExistingSections();
                
                // Optimisation : utiliser les données pré-construites si disponibles
                const hierarchyElement = document.getElementById('category-hierarchy-data');
                if (hierarchyElement) {
                    // Présélection immédiate avec les données pré-construites
                    setTimeout(() => {
                        preselectCategory(courseData.categoryid);
                    }, 50);
                } else {
                    // Fallback vers l'ancienne méthode
                    setTimeout(() => {
                        preselectCategory(courseData.categoryid);
                    }, 100);
                }
            }
        }
    }

    function loadExistingSections() {
        const sectionsDataElement = document.getElementById('course-sections-data');
        if (sectionsDataElement) {
            const sectionElements = sectionsDataElement.querySelectorAll('.section-data');
            
            sectionElements.forEach((sectionElement, index) => {
                const sectionData = {
                    id: sectionElement.dataset.id,
                    name: sectionElement.dataset.name,
                    summary: sectionElement.dataset.summary
                };
                
                // Filtrer les sections "Généralités" - elles ne doivent pas apparaître dans l'interface d'édition
                const sectionName = sectionData.name ? sectionData.name.trim().toLowerCase() : '';
                if (sectionName === 'généralités' || sectionName === 'generalites' || sectionName === 'general') {
                    return; // Ignorer cette section
                }
                
                // Récupérer les modules de cette section
                const moduleElements = sectionElement.querySelectorAll('.module-data');
                const modules = Array.from(moduleElements).map(moduleEl => ({
                    id: moduleEl.dataset.id,
                    name: moduleEl.dataset.name,
                    modname: moduleEl.dataset.modname,
                    url: moduleEl.dataset.url,
                    description: moduleEl.dataset.description
                }));
                
                // Créer la section dans l'interface SEULEMENT si ce n'est pas la section générale
                if (sectionData.name && sectionData.name.trim()) {
                    sectionCounter++;
                    const sectionItem = createSectionElementWithData(sectionCounter, sectionData, modules);
                    sectionsList.appendChild(sectionItem);
                    
                    // Animation d'apparition
                    setTimeout(() => {
                        sectionItem.style.opacity = '1';
                        sectionItem.style.transform = 'translateY(0)';
                    }, 10);
                }
            });
        }
    }

    function createSectionElementWithData(sectionNumber, sectionData, modules = []) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section-item';
        sectionDiv.style.opacity = '0';
        sectionDiv.style.transform = 'translateY(-20px)';
        sectionDiv.style.transition = 'all 0.3s ease';
        
        // Créer la liste des ressources existantes
        let resourcesHtml = '';
        modules.forEach(module => {
            if (module.name && module.name.trim()) {
                resourcesHtml += `
                    <div class="existing-resource">
                        ${module.url ? `<a href="${module.url}" target="_blank" class="resource-link">🔗</a>` : ''}
                        <span class="resource-name">${module.name}</span>
                        <span class="resource-type">(${module.modname || 'Ressource'})</span>
                    </div>
                `;
            }
        });
        
        sectionDiv.innerHTML = `
            <div class="section-header-item">
                <div class="section-number">${sectionNumber}</div>
                <input type="text" 
                       name="section_${sectionNumber}" 
                       value="${sectionData.name || ''}"
                       placeholder="Titre de la section ${sectionNumber}" 
                       required 
                       class="section-title-input">
                <button type="button" class="delete-section-btn" onclick="deleteSection(this)">
                    ✕
                </button>
            </div>
            ${resourcesHtml ? `<div class="existing-resources">${resourcesHtml}</div>` : ''}
            <div class="section-actions">
                <button type="button" class="resource-btn" onclick="addResource(this, ${sectionNumber})">
                    Ajouter une ressource
                </button>
                <input type="hidden" name="file_${sectionNumber}" id="file_${sectionNumber}">
                <span class="selected-file" id="selected-file-${sectionNumber}"></span>
            </div>
        `;
        
        return sectionDiv;
    }

    function preselectCategory(categoryId) {
        if (!categoryId) return Promise.resolve();
        
        // Utiliser directement les données de présélection du backend
        const preselectionData = getPreselectionData();
        if (preselectionData && preselectionData.target_category_id == categoryId) {
            return preselectFromOptimizedData(preselectionData);
        } else {
            return Promise.resolve();
        }
    }

    function getPreselectionData() {
        const preselectionElement = document.getElementById('preselection-data');
        if (preselectionElement) {
            try {
                return JSON.parse(preselectionElement.textContent);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    function preselectFromOptimizedData(data) {
        
        try {
            const { path, years, formations } = data;
            
            if (!path || path.length === 0) {
                return Promise.resolve();
            }
            
            // Attendre que les catégories principales soient chargées avant de présélectionner
            return new Promise((resolve) => {
                const waitForSchools = () => {
                    const schoolSelect = categorySelects[0];
                    
                    // Vérifier si les écoles sont déjà chargées
                    if (schoolSelect.options.length > 1) {
                        doPreselection();
                        resolve();
                    } else {
                        // Attendre un peu et réessayer
                        setTimeout(waitForSchools, 50);
                    }
                };
                
                const doPreselection = () => {
                    // École (niveau 0)
                    if (path.length >= 1) {
                        const school = path[0];
                        categorySelects[0].value = school.id;
                        categorySelects[0].classList.remove('hidden');
                        
                        // Année (niveau 1)
                        if (path.length >= 2 && years && years.length > 0) {
                            const year = path[1];
                            
                            const yearSelect = categorySelects[1];
                            yearSelect.innerHTML = '<option value="">Sélectionnez...</option>';
                            years.forEach(y => {
                                const option = new Option(y.name, y.id);
                                yearSelect.add(option);
                            });
                            yearSelect.classList.remove('hidden');
                            yearSelect.value = year.id;
                            
                            // Formation (niveau 2)
                            if (path.length >= 3 && formations && formations.length > 0) {
                                const formation = path[2];
                                
                                const formationSelect = categorySelects[2];
                                formationSelect.innerHTML = '<option value="">Sélectionnez...</option>';
                                formations.forEach(f => {
                                    const option = new Option(f.name, f.id);
                                    formationSelect.add(option);
                                });
                                formationSelect.classList.remove('hidden');
                                formationSelect.value = formation.id;
                            }
                        }
                    }
                };
                
                waitForSchools();
            });
            
        } catch (error) {
            return Promise.reject(error);
        }
    }

    // Initialiser le mode édition si nécessaire
    initEditMode();
});
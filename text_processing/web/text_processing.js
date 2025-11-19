import { app } from "../../../../scripts/app.js";

// 为文本分割器节点添加自定义UI
app.registerExtension({
    name: "Zhuge.TextSplitter",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ZhugeTextSplitter") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this) : undefined;
                
                // 添加重置按钮
                const button = document.createElement("button");
                button.textContent = "重置索引";
                button.style.marginTop = "10px";
                button.style.padding = "5px";
                button.style.width = "100%";
                button.style.backgroundColor = "#4a4a4a";
                button.style.color = "white";
                button.style.border = "none";
                button.style.borderRadius = "3px";
                button.style.cursor = "pointer";
                
                button.addEventListener("click", () => {
                    // 设置重置标志
                    this.widgets.forEach(w => {
                        if (w.name === "reset") {
                            w.value = true;
                        }
                    });
                    // 触发执行
                    app.graph.setDirtyCanvas(true, true);
                });
                
                this.addDOMWidget("reset_button", "button", button, {
                    getValue: () => {},
                    setValue: () => {}
                });
                
                // 添加状态显示
                const statusContainer = document.createElement("div");
                statusContainer.style.marginTop = "10px";
                statusContainer.style.padding = "5px";
                statusContainer.style.backgroundColor = "#333";
                statusContainer.style.borderRadius = "3px";
                statusContainer.style.fontSize = "12px";
                statusContainer.style.textAlign = "center";
                statusContainer.textContent = "就绪";
                
                this.addDOMWidget("status_display", "status", statusContainer, {
                    getValue: () => {},
                    setValue: () => {}
                });
                
                this.statusDisplay = statusContainer;
                
                return result;
            };
            
            // 更新状态显示
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                const result = onExecuted ? onExecuted.apply(this, [message]) : undefined;
                
                if (message && this.statusDisplay) {
                    const currentIndex = message.current_index || 0;
                    const totalCount = message.total_count || 1;
                    const hasMore = message.has_more || false;
                    
                    if (totalCount > 0) {
                        const status = hasMore ? 
                            `处理中: ${currentIndex + 1}/${totalCount}` : 
                            `完成: ${currentIndex + 1}/${totalCount}`;
                        this.statusDisplay.textContent = status;
                        this.statusDisplay.style.backgroundColor = hasMore ? "#555" : "#2a5c2a";
                    }
                    
                    // 自动重置重置按钮
                    this.widgets.forEach(w => {
                        if (w.name === "reset") {
                            w.value = false;
                        }
                    });
                }
                
                return result;
            };
        }
    }
});

// 为文本分割信息节点添加样式
app.registerExtension({
    name: "Zhuge.TextSplitInfo",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ZhugeTextSplitInfo") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this) : undefined;
                
                // 添加统计信息显示
                const infoContainer = document.createElement("div");
                infoContainer.style.marginTop = "10px";
                infoContainer.style.padding = "5px";
                infoContainer.style.backgroundColor = "#2a2a4a";
                infoContainer.style.borderRadius = "3px";
                infoContainer.style.fontSize = "12px";
                infoContainer.style.textAlign = "center";
                infoContainer.textContent = "等待输入...";
                
                this.addDOMWidget("info_display", "info", infoContainer, {
                    getValue: () => {},
                    setValue: () => {}
                });
                
                this.infoDisplay = infoContainer;
                
                return result;
            };
            
            // 更新信息显示
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                const result = onExecuted ? onExecuted.apply(this, [message]) : undefined;
                
                if (message && this.infoDisplay) {
                    const totalCount = message.total_count || 0;
                    this.infoDisplay.textContent = `总行数: ${totalCount}`;
                    this.infoDisplay.style.backgroundColor = totalCount > 0 ? "#2a5c2a" : "#5c2a2a";
                }
                
                return result;
            };
        }
    }
});
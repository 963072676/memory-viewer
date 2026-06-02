User operates Hermes on ZOS host 192.168.5.55:20200 (Docker container). Prefers Chinese, concise responses. Dev reports go to feishu:开发团队 group, not DM.
§
沟通风格：中文，简洁但不遗漏重点。
§
chief-agent 是编排层，不直接做代码/用例/测试/详细需求。实质性工作必须通过 kanban 组织团队（delegate_task）完成。用户会主动检查角色是否越权，发现违规直接指出。
§
用户在中国重庆，全部使用北京时间（Asia/Shanghai，UTC+8）。中文交流，简洁直接风格。
§
When asking for system/config changes, user prefers direct execution over guidance-only, with backup+rollback for restart-impacting changes. "你自己上去弄" = do it directly, don't offer commands. Repeated request = take action (re-verify/re-run), never explain "already done". "？" = impatience/confusion → move to next step, don't clarify.
§
版本检查必须真正执行 git fetch + 比较 HEAD vs origin，不能凭缓存或本地状态判断"已是最新"。用户会质疑并要求重新验证。
§
User manages 5 Hermes profiles: chief-agent (mimo-v2.5-pro, main), daily (MiniMax-M2.7, kept intentionally), dev-worker/pm-orchestrator/qa-worker (mimo-v2.5-pro). daily is explicitly kept on MiniMax-M2.7 as a separate model for daily use.
§
开发相关汇报（迭代进度、自驱动循环输出等）发到飞书"开发团队"群聊（feishu:开发团队），不私聊打扰。私聊只做配置和紧急沟通。
§
用户要求"彻底清理"时期望所有相关文件、配置、skill 引用全部移除，不只是禁用。
§
用户偏好自主执行模式：说"你通过自驱动，自己规划方案然后落地"时，跳过逐项确认，PM 规划后直接派发 DEV+QA，结果汇报即可。适用于长期项目迭代。
§
用户偏好自驱动工作模式：让 chief-agent 自己规划方案然后落地，不需要每步确认。明确说过"你通过自驱动，自己规划方案然后落地，满足我上述要求即可"。对快速决策风格（"好"、"继续"、选数字）非常高效。
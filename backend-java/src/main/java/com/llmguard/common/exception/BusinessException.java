/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.common.exception;

/**
 * 功能描述：业务异常类，用于业务逻辑校验失败时抛出
 *
 * @date 2024/07/13 16:06
 */
public class BusinessException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    private final int code;
    private final String msg;

    /**
     * 构造业务异常
     *
     * @param code 错误码
     * @param msg  错误描述
     */
    public BusinessException(int code, String msg) {
        super(msg);
        this.code = code;
        this.msg = msg;
    }

    /**
     * 构造业务异常（默认错误码400）
     *
     * @param msg 错误描述
     */
    public BusinessException(String msg) {
        super(msg);
        this.code = 400;
        this.msg = msg;
    }

    public int getCode() {
        return code;
    }

    public String getMsg() {
        return msg;
    }
}

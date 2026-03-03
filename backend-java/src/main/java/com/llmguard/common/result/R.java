/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
package com.llmguard.common.result;

import java.io.Serializable;

/**
 * 功能描述：统一响应封装类
 *
 * @date 2024/07/13 16:06
 */
public class R<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    private boolean success;
    private int code;
    private String msg;
    private T data;

    public R() {
    }

    private R(boolean success, int code, String msg, T data) {
        this.success = success;
        this.code = code;
        this.msg = msg;
        this.data = data;
    }

    /**
     * 成功响应（带数据）
     *
     * @param data 响应数据
     * @param <T>  数据类型
     * @return 统一响应对象
     */
    public static <T> R<T> ok(T data) {
        return new R<>(true, 200, "success", data);
    }

    /**
     * 成功响应（无数据）
     *
     * @param <T> 数据类型
     * @return 统一响应对象
     */
    public static <T> R<T> ok() {
        return new R<>(true, 200, "success", null);
    }

    /**
     * 失败响应
     *
     * @param code 错误码
     * @param msg  错误信息
     * @param <T>  数据类型
     * @return 统一响应对象
     */
    public static <T> R<T> fail(int code, String msg) {
        return new R<>(false, code, msg, null);
    }

    /**
     * 失败响应（默认500）
     *
     * @param msg 错误信息
     * @param <T> 数据类型
     * @return 统一响应对象
     */
    public static <T> R<T> fail(String msg) {
        return new R<>(false, 500, msg, null);
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }
}

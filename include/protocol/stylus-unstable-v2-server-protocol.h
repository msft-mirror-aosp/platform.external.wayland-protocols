/* Generated by wayland-scanner 1.13.0 */

#ifndef STYLUS_UNSTABLE_V2_SERVER_PROTOCOL_H
#define STYLUS_UNSTABLE_V2_SERVER_PROTOCOL_H

#include <stdint.h>
#include <stddef.h>
#include "wayland-server.h"

#ifdef  __cplusplus
extern "C" {
#endif

struct wl_client;
struct wl_resource;

/**
 * @page page_stylus_unstable_v2 The stylus_unstable_v2 protocol
 * @section page_ifaces_stylus_unstable_v2 Interfaces
 * - @subpage page_iface_zcr_stylus_v2 - extends wl_touch with events for on-screen stylus
 * - @subpage page_iface_zcr_touch_stylus_v2 - stylus extension for touch
 * @section page_copyright_stylus_unstable_v2 Copyright
 * <pre>
 *
 * Copyright 2016 The Chromium Authors.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 * </pre>
 */
struct wl_touch;
struct zcr_stylus_v2;
struct zcr_touch_stylus_v2;

/**
 * @page page_iface_zcr_stylus_v2 zcr_stylus_v2
 * @section page_iface_zcr_stylus_v2_desc Description
 *
 * Allows a wl_touch to report stylus specific information. The client can
 * interpret the on-screen stylus like any other touch event, and use
 * this protocol to obtain detail information about the type of stylus,
 * as well as the force and tilt of the tool.
 *
 * These events are to be fired by the server within the same frame as other
 * wl_touch events.
 *
 * Warning! The protocol described in this file is experimental and
 * backward incompatible changes may be made. Backward compatible changes
 * may be added together with the corresponding uinterface version bump.
 * Backward incompatible changes are done by bumping the version number in
 * the protocol and uinterface names and resetting the interface version.
 * Once the protocol is to be declared stable, the 'z' prefix and the
 * version number in the protocol and interface names are removed and the
 * interface version number is reset.
 * @section page_iface_zcr_stylus_v2_api API
 * See @ref iface_zcr_stylus_v2.
 */
/**
 * @defgroup iface_zcr_stylus_v2 The zcr_stylus_v2 interface
 *
 * Allows a wl_touch to report stylus specific information. The client can
 * interpret the on-screen stylus like any other touch event, and use
 * this protocol to obtain detail information about the type of stylus,
 * as well as the force and tilt of the tool.
 *
 * These events are to be fired by the server within the same frame as other
 * wl_touch events.
 *
 * Warning! The protocol described in this file is experimental and
 * backward incompatible changes may be made. Backward compatible changes
 * may be added together with the corresponding uinterface version bump.
 * Backward incompatible changes are done by bumping the version number in
 * the protocol and uinterface names and resetting the interface version.
 * Once the protocol is to be declared stable, the 'z' prefix and the
 * version number in the protocol and interface names are removed and the
 * interface version number is reset.
 */
extern const struct wl_interface zcr_stylus_v2_interface;
/**
 * @page page_iface_zcr_touch_stylus_v2 zcr_touch_stylus_v2
 * @section page_iface_zcr_touch_stylus_v2_desc Description
 *
 * The zcr_touch_stylus_v1 interface extends the wl_touch interface with
 * events to describe details about a stylus.
 * @section page_iface_zcr_touch_stylus_v2_api API
 * See @ref iface_zcr_touch_stylus_v2.
 */
/**
 * @defgroup iface_zcr_touch_stylus_v2 The zcr_touch_stylus_v2 interface
 *
 * The zcr_touch_stylus_v1 interface extends the wl_touch interface with
 * events to describe details about a stylus.
 */
extern const struct wl_interface zcr_touch_stylus_v2_interface;

#ifndef ZCR_STYLUS_V2_ERROR_ENUM
#define ZCR_STYLUS_V2_ERROR_ENUM
enum zcr_stylus_v2_error {
	/**
	 * the touch already has a touch_stylus object associated
	 */
	ZCR_STYLUS_V2_ERROR_TOUCH_STYLUS_EXISTS = 0,
};
#endif /* ZCR_STYLUS_V2_ERROR_ENUM */

/**
 * @ingroup iface_zcr_stylus_v2
 * @struct zcr_stylus_v2_interface
 */
struct zcr_stylus_v2_interface {
	/**
	 * get stylus interface for touch
	 *
	 * Create touch_stylus object. See zcr_touch_stylus_v1 interface
	 * for details. If the given wl_touch already has a touch_stylus
	 * object associated, the touch_stylus_exists protocol error is
	 * raised.
	 */
	void (*get_touch_stylus)(struct wl_client *client,
				 struct wl_resource *resource,
				 uint32_t id,
				 struct wl_resource *touch);
};


/**
 * @ingroup iface_zcr_stylus_v2
 */
#define ZCR_STYLUS_V2_GET_TOUCH_STYLUS_SINCE_VERSION 1

#ifndef ZCR_TOUCH_STYLUS_V2_TOOL_TYPE_ENUM
#define ZCR_TOUCH_STYLUS_V2_TOOL_TYPE_ENUM
/**
 * @ingroup iface_zcr_touch_stylus_v2
 * tool type of device.
 */
enum zcr_touch_stylus_v2_tool_type {
	/**
	 * Touch
	 */
	ZCR_TOUCH_STYLUS_V2_TOOL_TYPE_TOUCH = 1,
	/**
	 * Pen
	 */
	ZCR_TOUCH_STYLUS_V2_TOOL_TYPE_PEN = 2,
	/**
	 * Eraser
	 */
	ZCR_TOUCH_STYLUS_V2_TOOL_TYPE_ERASER = 3,
};
#endif /* ZCR_TOUCH_STYLUS_V2_TOOL_TYPE_ENUM */

/**
 * @ingroup iface_zcr_touch_stylus_v2
 * @struct zcr_touch_stylus_v2_interface
 */
struct zcr_touch_stylus_v2_interface {
	/**
	 * destroy stylus object
	 *
	 * 
	 */
	void (*destroy)(struct wl_client *client,
			struct wl_resource *resource);
};

#define ZCR_TOUCH_STYLUS_V2_TOOL 0
#define ZCR_TOUCH_STYLUS_V2_FORCE 1
#define ZCR_TOUCH_STYLUS_V2_TILT 2

/**
 * @ingroup iface_zcr_touch_stylus_v2
 */
#define ZCR_TOUCH_STYLUS_V2_TOOL_SINCE_VERSION 1
/**
 * @ingroup iface_zcr_touch_stylus_v2
 */
#define ZCR_TOUCH_STYLUS_V2_FORCE_SINCE_VERSION 1
/**
 * @ingroup iface_zcr_touch_stylus_v2
 */
#define ZCR_TOUCH_STYLUS_V2_TILT_SINCE_VERSION 1

/**
 * @ingroup iface_zcr_touch_stylus_v2
 */
#define ZCR_TOUCH_STYLUS_V2_DESTROY_SINCE_VERSION 1

/**
 * @ingroup iface_zcr_touch_stylus_v2
 * Sends an tool event to the client owning the resource.
 * @param resource_ The client's resource
 * @param id touch id
 * @param type type of tool in use
 */
static inline void
zcr_touch_stylus_v2_send_tool(struct wl_resource *resource_, uint32_t id, uint32_t type)
{
	wl_resource_post_event(resource_, ZCR_TOUCH_STYLUS_V2_TOOL, id, type);
}

/**
 * @ingroup iface_zcr_touch_stylus_v2
 * Sends an force event to the client owning the resource.
 * @param resource_ The client's resource
 * @param time timestamp with millisecond granularity
 * @param id touch id
 * @param force new value of force
 */
static inline void
zcr_touch_stylus_v2_send_force(struct wl_resource *resource_, uint32_t time, uint32_t id, wl_fixed_t force)
{
	wl_resource_post_event(resource_, ZCR_TOUCH_STYLUS_V2_FORCE, time, id, force);
}

/**
 * @ingroup iface_zcr_touch_stylus_v2
 * Sends an tilt event to the client owning the resource.
 * @param resource_ The client's resource
 * @param time timestamp with millisecond granularity
 * @param id touch id
 * @param tilt_x tilt in x direction
 * @param tilt_y tilt in y direction
 */
static inline void
zcr_touch_stylus_v2_send_tilt(struct wl_resource *resource_, uint32_t time, uint32_t id, wl_fixed_t tilt_x, wl_fixed_t tilt_y)
{
	wl_resource_post_event(resource_, ZCR_TOUCH_STYLUS_V2_TILT, time, id, tilt_x, tilt_y);
}

#ifdef  __cplusplus
}
#endif

#endif

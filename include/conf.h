/**
 * \file <alsa/conf.h>
 * \brief Application interface library for the ALSA driver
 * \author Jaroslav Kysela <perex@suse.cz>
 * \author Abramo Bagnara <abramo@alsa-project.org>
 * \author Takashi Iwai <tiwai@suse.de>
 * \date 1998-2001
 *
 * Application interface library for the ALSA driver
 *
 *
 *   This library is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU Library General Public License as
 *   published by the Free Software Foundation; either version 2 of
 *   the License, or (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Library General Public License for more details.
 *
 *   You should have received a copy of the GNU Library General Public
 *   License along with this library; if not, write to the Free Software
 *   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 */

#ifndef __ALSA_CONF_H
#define __ALSA_CONF_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 *  \defgroup Config Configuration Interface
 *  Configuration Interface
 *  \{
 */

/** dlsym version for config evaluate callback */
#define SND_CONFIG_DLSYM_VERSION_EVALUATE	_dlsym_config_evaluate_001
/** dlsym version for config hook callback */
#define SND_CONFIG_DLSYM_VERSION_HOOK		_dlsym_config_hook_001

/** Config node type */
typedef enum _snd_config_type {
	/** Integer number */
        SND_CONFIG_TYPE_INTEGER,
	/** Real number */
        SND_CONFIG_TYPE_REAL,
	/** Character string */
        SND_CONFIG_TYPE_STRING,
        /** Pointer - runtime only - cannot be saved */
        SND_CONFIG_TYPE_POINTER,
	/** Compound */
	SND_CONFIG_TYPE_COMPOUND = 1024,
} snd_config_type_t;

/** Config node handle */
typedef struct _snd_config snd_config_t;
/** Config compound iterator */
typedef struct _snd_config_iterator *snd_config_iterator_t;

extern snd_config_t *snd_config;

int snd_config_top(snd_config_t **config);

int snd_config_load(snd_config_t *config, snd_input_t *in);
int snd_config_save(snd_config_t *config, snd_output_t *out);
int snd_config_update(void);

int snd_config_search(snd_config_t *config, const char *key,
		      snd_config_t **result);
int snd_config_searchv(snd_config_t *config, 
		       snd_config_t **result, ...);
int snd_config_search_definition(snd_config_t *config,
				 const char *base, const char *key,
				 snd_config_t **result);

int snd_config_expand(snd_config_t *config, snd_config_t *root,
		      const char *args, snd_config_t *private_data,
		      snd_config_t **result);
int snd_config_evaluate(snd_config_t *config, snd_config_t *root,
			snd_config_t *private_data, snd_config_t **result);

int snd_config_add(snd_config_t *config, snd_config_t *leaf);
int snd_config_delete(snd_config_t *config);
int snd_config_copy(snd_config_t **dst, snd_config_t *src);

int snd_config_make(snd_config_t **config, const char *key,
		    snd_config_type_t type);
int snd_config_make_integer(snd_config_t **config, const char *key);
int snd_config_make_real(snd_config_t **config, const char *key);
int snd_config_make_string(snd_config_t **config, const char *key);
int snd_config_make_pointer(snd_config_t **config, const char *key);
int snd_config_make_compound(snd_config_t **config, const char *key, int join);

int snd_config_imake_integer(snd_config_t **config, const char *key, const long value);
int snd_config_imake_real(snd_config_t **config, const char *key, const double value);
int snd_config_imake_string(snd_config_t **config, const char *key, const char *ascii);
int snd_config_imake_pointer(snd_config_t **config, const char *key, const void *ptr);

snd_config_type_t snd_config_get_type(snd_config_t *config);

int snd_config_set_id(snd_config_t *config, const char *id);
int snd_config_set_integer(snd_config_t *config, long value);
int snd_config_set_real(snd_config_t *config, double value);
int snd_config_set_string(snd_config_t *config, const char *value);
int snd_config_set_ascii(snd_config_t *config, const char *ascii);
int snd_config_set_pointer(snd_config_t *config, const void *ptr);
int snd_config_get_id(snd_config_t *config, const char **value);
int snd_config_get_integer(snd_config_t *config, long *value);
int snd_config_get_real(snd_config_t *config, double *value);
int snd_config_get_ireal(snd_config_t *config, double *value);
int snd_config_get_string(snd_config_t *config, const char **value);
int snd_config_get_ascii(snd_config_t *config, char **value);
int snd_config_get_pointer(snd_config_t *config, const void **value);
int snd_config_test_id(snd_config_t *config, const char *id);

snd_config_iterator_t snd_config_iterator_first(snd_config_t *node);
snd_config_iterator_t snd_config_iterator_next(snd_config_iterator_t iterator);
snd_config_iterator_t snd_config_iterator_end(snd_config_t *node);
snd_config_t *snd_config_iterator_entry(snd_config_iterator_t iterator);

/** Helper for compound config node leaves traversal
 * \param pos Current node iterator
 * \param next Next node iterator
 * \param node Compound config node
 *
 * This macro is designed to permit the removal of current node.
 */
#define snd_config_for_each(pos, next, node) \
	for (pos = snd_config_iterator_first(node), next = snd_config_iterator_next(pos); pos != snd_config_iterator_end(node); pos = next, next = snd_config_iterator_next(pos))

/* Misc functions */

int snd_config_get_bool_ascii(const char *ascii);
int snd_config_get_bool(snd_config_t *conf);
int snd_config_get_ctl_iface_ascii(const char *ascii);
int snd_config_get_ctl_iface(snd_config_t *conf);

/** \} */

#ifdef __cplusplus
}
#endif

#endif /* __ALSA_CONF_H */


import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  UpdateFieldLevelEncryptionConfigRequest,
  UpdateFieldLevelEncryptionConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateFieldLevelEncryptionConfigCommandInput
  extends UpdateFieldLevelEncryptionConfigRequest {}
export interface UpdateFieldLevelEncryptionConfigCommandOutput
  extends UpdateFieldLevelEncryptionConfigResult,
    __MetadataBearer {}
export declare class UpdateFieldLevelEncryptionConfigCommand extends $Command<
  UpdateFieldLevelEncryptionConfigCommandInput,
  UpdateFieldLevelEncryptionConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateFieldLevelEncryptionConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateFieldLevelEncryptionConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateFieldLevelEncryptionConfigCommandInput,
    UpdateFieldLevelEncryptionConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
